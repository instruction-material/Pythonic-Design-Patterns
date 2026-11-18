"""Public order-event delivery and ownership contracts for both roles."""
import asyncio
from dataclasses import FrozenInstanceError
import gc
import unittest
import warnings
import weakref
from main import AsyncEventBus, EventBus, OrderEvent, build_order_event

CHANNEL = "order.updated"
EVENT = build_order_event("ready")


class SynchronousDelivery(unittest.TestCase):
    def test_empty_order_and_duplicate_connections(self):
        bus, seen = EventBus(), []
        bus.publish(CHANNEL, EVENT)
        def record(event): seen.append(event.status)
        first, second = bus.subscribe(CHANNEL, record), bus.subscribe(CHANNEL, record)
        self.assertIsInstance(first, int)
        self.assertNotEqual(first, second)
        bus.publish(CHANNEL, EVENT)
        self.assertEqual(seen, ["ready", "ready"])
        bus.unsubscribe(CHANNEL, first)
        bus.unsubscribe(CHANNEL, first)
        bus.publish(CHANNEL, build_order_event("later"))
        self.assertEqual(seen, ["ready", "ready", "later"])

    def test_removal_and_addition_use_one_publication_snapshot(self):
        bus, seen, changed = EventBus(), [], []
        def later(event): seen.append("later")
        def first(event):
            seen.append("first")
            if not changed:
                bus.unsubscribe(CHANNEL, second)
                bus.subscribe(CHANNEL, later)
                changed.append(True)
        def other(event): seen.append("second")
        bus.subscribe(CHANNEL, first)
        second = bus.subscribe(CHANNEL, other)
        bus.publish(CHANNEL, EVENT)
        self.assertEqual(seen, ["first", "second"])
        seen.clear()
        bus.publish(CHANNEL, EVENT)
        self.assertEqual(seen, ["first", "later"])

    def test_nested_publication_is_depth_first_with_its_own_snapshot(self):
        bus, seen = EventBus(), []
        def first(event):
            seen.append("a:" + event.status)
            if event.status == "outer":
                bus.publish(CHANNEL, build_order_event("inner"))
        def second(event): seen.append("b:" + event.status)
        bus.subscribe(CHANNEL, first)
        bus.subscribe(CHANNEL, second)
        bus.publish(CHANNEL, build_order_event("outer"))
        self.assertEqual(seen, ["a:outer", "a:inner", "b:inner", "b:outer"])

    def test_handle_disconnects_on_exception_and_never_reconnects(self):
        bus, seen = EventBus(), []
        failure = LookupError("body")
        with self.assertRaises(LookupError) as caught:
            with bus.connect(CHANNEL, lambda event: seen.append(event.status)) as handle:
                bus.publish(CHANNEL, EVENT)
                raise failure
        self.assertIs(caught.exception, failure)
        handle.close()
        with handle:
            bus.publish(CHANNEL, EVENT)
        self.assertEqual(seen, ["ready"])

    def test_dead_weak_method_is_not_retained(self):
        bus, seen = EventBus(), []
        class Owner:
            def receive(self, event): seen.append(event.status)
        owner = Owner()
        ref = weakref.ref(owner)
        bus.subscribe(CHANNEL, owner.receive, weak=True)
        bus.publish(CHANNEL, EVENT)
        del owner
        gc.collect()
        self.assertIsNone(ref())
        bus.publish(CHANNEL, EVENT)
        self.assertEqual(seen, ["ready"])
        with self.assertRaises(TypeError):
            bus.subscribe(CHANNEL, lambda event: None, weak=True)

    def test_failure_stops_delivery_and_keeps_original_exception(self):
        bus, seen = EventBus(), []
        failure = OSError("listener broke")
        def fail(event):
            seen.append("failed")
            raise failure
        bus.subscribe(CHANNEL, fail)
        bus.subscribe(CHANNEL, lambda event: seen.append("later"))
        with self.assertRaises(OSError) as caught:
            bus.publish(CHANNEL, EVENT)
        self.assertIs(caught.exception, failure)
        self.assertEqual(seen, ["failed"])

    def test_invalid_channels_payloads_and_sync_coroutines(self):
        bus = EventBus()
        for channel in ["", " "]:
            with self.assertRaises(ValueError): bus.subscribe(channel, lambda event: None)
        for value in [None, True, 2]:
            with self.assertRaises(TypeError): bus.subscribe(value, lambda event: None)
        with self.assertRaises(TypeError): bus.subscribe(CHANNEL, None)
        with self.assertRaises(TypeError): bus.publish(CHANNEL, {})
        for fields in [("", "ready", "x"), ("1", " ", "x"), ("1", "ready", "")]:
            with self.assertRaises(ValueError): OrderEvent(*fields)
        async def asynchronous(event): pass
        with self.assertRaises(TypeError): bus.subscribe(CHANNEL, asynchronous)
        with warnings.catch_warnings(record=True) as recorded:
            warnings.simplefilter("always")
            bus.subscribe(CHANNEL, lambda event: asynchronous(event))
            with self.assertRaises(TypeError): bus.publish(CHANNEL, EVENT)
            gc.collect()
        self.assertFalse([w for w in recorded if issubclass(w.category, RuntimeWarning)])

    def test_bus_close_is_idempotent_and_handles_can_still_disconnect(self):
        bus = EventBus()
        handle = bus.connect(CHANNEL, lambda event: None)
        bus.close()
        bus.close()
        handle.close()
        bus.unsubscribe("unknown", 999)
        with self.assertRaises(RuntimeError): bus.publish(CHANNEL, EVENT)
        with self.assertRaises(RuntimeError): bus.subscribe(CHANNEL, lambda event: None)

    def test_payload_is_immutable_and_strong_connections_own_their_listener(self):
        with self.assertRaises(FrozenInstanceError): EVENT.status = "changed"
        bus = EventBus()
        class Owner:
            def receive(self, event): pass
        owner = Owner()
        ref = weakref.ref(owner)
        handle = bus.connect(CHANNEL, owner.receive)
        del owner
        gc.collect()
        self.assertIsNotNone(ref())
        handle.close()
        gc.collect()
        self.assertIsNone(ref())

    def test_a_live_weak_method_is_retained_for_the_captured_delivery(self):
        bus, seen = EventBus(), []
        class Owner:
            def receive(self, event): seen.append("owner")
        box = [Owner()]
        ref = weakref.ref(box[0])
        def first(event):
            seen.append("first")
            box.clear()
            gc.collect()
        bus.subscribe(CHANNEL, first)
        bus.subscribe(CHANNEL, box[0].receive, weak=True)
        bus.publish(CHANNEL, EVENT)
        self.assertEqual(seen, ["first", "owner"])
        self.assertIsNone(ref())
        seen.clear()
        bus.publish(CHANNEL, EVENT)
        self.assertEqual(seen, ["first"])


class AsynchronousDelivery(unittest.IsolatedAsyncioTestCase):
    async def test_serial_order_empty_channel_and_no_bus_created_tasks(self):
        bus, seen = AsyncEventBus(), []
        before = asyncio.all_tasks()
        await bus.publish(CHANNEL, EVENT)
        async def first(event):
            seen.append("a:start")
            await asyncio.sleep(0)
            seen.append("a:end")
        async def second(event): seen.append("b")
        bus.subscribe(CHANNEL, first)
        bus.subscribe(CHANNEL, second)
        await bus.publish(CHANNEL, EVENT)
        self.assertEqual(seen, ["a:start", "a:end", "b"])
        self.assertEqual(asyncio.all_tasks(), before)
        bus.close()

    async def test_async_snapshot_duplicate_and_explicit_lifetime(self):
        bus, seen, added = AsyncEventBus(), [], []
        async def later(event): seen.append("later")
        async def first(event):
            seen.append("first")
            handle.close()
            if not added:
                bus.subscribe(CHANNEL, later)
                added.append(True)
        async def second(event): seen.append("second")
        bus.subscribe(CHANNEL, first)
        handle = bus.connect(CHANNEL, second)
        bus.subscribe(CHANNEL, second)
        await bus.publish(CHANNEL, EVENT)
        self.assertEqual(seen, ["first", "second", "second"])
        seen.clear()
        await bus.publish(CHANNEL, EVENT)
        self.assertEqual(seen, ["first", "second", "later"])
        bus.close()

    async def test_async_failure_and_nonawaitable_callback_stop(self):
        bus, seen = AsyncEventBus(), []
        failure = LookupError("async failure")
        async def fail(event):
            seen.append("failure")
            raise failure
        async def later(event): seen.append("later")
        bus.subscribe(CHANNEL, fail)
        bus.subscribe(CHANNEL, later)
        with self.assertRaises(LookupError) as caught:
            await bus.publish(CHANNEL, EVENT)
        self.assertIs(caught.exception, failure)
        self.assertEqual(seen, ["failure"])
        bus.close()
        invalid = AsyncEventBus()
        invalid.subscribe(CHANNEL, lambda event: None)
        with self.assertRaises(TypeError): await invalid.publish(CHANNEL, EVENT)
        invalid.close()

    async def test_cancellation_is_awaited_before_idle_shutdown(self):
        bus, seen = AsyncEventBus(), []
        started, release = asyncio.Event(), asyncio.Event()
        async def wait(event):
            seen.append("start")
            started.set()
            try: await release.wait()
            finally: seen.append("cleanup")
        async def later(event): seen.append("later")
        bus.subscribe(CHANNEL, wait)
        bus.subscribe(CHANNEL, later)
        task = asyncio.create_task(bus.publish(CHANNEL, EVENT))
        try:
            await asyncio.wait_for(started.wait(), 2)
            with self.assertRaises(RuntimeError): bus.close()
        finally:
            task.cancel()
            with self.assertRaises(asyncio.CancelledError): await task
        self.assertEqual(seen, ["start", "cleanup"])
        bus.close()
        with self.assertRaises(RuntimeError): await bus.publish(CHANNEL, EVENT)

    async def test_overlapping_and_nested_async_publications_are_rejected(self):
        bus, started, release = AsyncEventBus(), asyncio.Event(), asyncio.Event()
        seen = []
        async def wait(event):
            started.set()
            try: await release.wait()
            finally: seen.append("finished")
        bus.subscribe(CHANNEL, wait)
        task = asyncio.create_task(bus.publish(CHANNEL, EVENT))
        try:
            await asyncio.wait_for(started.wait(), 2)
            with self.assertRaises(RuntimeError): await bus.publish(CHANNEL, EVENT)
        finally:
            release.set()
            await task
        bus.close()
        nested = AsyncEventBus()
        async def reenter(event):
            with self.assertRaises(RuntimeError): await nested.publish(CHANNEL, EVENT)
            seen.append("nested rejected")
        nested.subscribe(CHANNEL, reenter)
        await nested.publish(CHANNEL, EVENT)
        self.assertEqual(seen, ["finished", "nested rejected"])
        nested.close()


if __name__ == "__main__":
    unittest.main()
