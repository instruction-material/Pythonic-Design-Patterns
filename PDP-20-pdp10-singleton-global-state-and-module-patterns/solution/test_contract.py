import asyncio
import importlib
import unittest
from contextvars import copy_context
import main as lab


class ContextContracts(unittest.TestCase):
    def tearDown(self):
        lab.clear_cache()

    def test_nested_tokens_restore_and_absence_is_explicit(self):
        with self.assertRaises(LookupError): lab.current_request()
        with lab.request_context("outer"):
            self.assertEqual(lab.current_request(), "outer")
            with lab.request_context("inner"):
                self.assertEqual(lab.current_request(), "inner")
            self.assertEqual(lab.current_request(), "outer")
        with self.assertRaises(LookupError): lab.current_request()

    def test_failure_reset_and_copied_context(self):
        error = RuntimeError("request failed")
        with self.assertRaises(RuntimeError) as caught:
            with lab.request_context("captured"):
                copied = copy_context()
                raise error
        self.assertIs(caught.exception, error)
        with self.assertRaises(LookupError): lab.current_request()
        self.assertEqual(copied.run(lab.current_request), "captured")
        def change_copy():
            with lab.request_context("changed"):
                return lab.current_request()
        self.assertEqual(copied.run(change_copy), "changed")
        self.assertEqual(copied.run(lab.current_request), "captured")

    def test_concurrent_tasks_and_cancellation_restore_context(self):
        async def worker(name):
            with lab.request_context(name):
                await asyncio.sleep(0)
                return lab.current_request()
        async def check():
            with lab.request_context("parent"):
                self.assertEqual(await asyncio.gather(worker("a"), worker("b")), ["a", "b"])
                self.assertEqual(lab.current_request(), "parent")
                entered = asyncio.Event()
                after_cancel = []
                async def cancellable():
                    try:
                        with lab.request_context("child"):
                            entered.set()
                            await asyncio.sleep(3600)
                    finally:
                        after_cancel.append(lab.current_request())
                task = asyncio.create_task(cancellable())
                await entered.wait()
                task.cancel()
                with self.assertRaises(asyncio.CancelledError): await task
                self.assertEqual(lab.current_request(), "parent")
                self.assertEqual(after_cancel, ["parent"])
        asyncio.run(check())
        with self.assertRaises(LookupError): lab.current_request()

    def test_reimport_shares_cache_until_explicit_teardown(self):
        first = importlib.import_module(lab.__name__)
        second = importlib.import_module(lab.__name__)
        self.assertIs(first, second)
        self.assertEqual(first.remember("key", "first"), "first")
        self.assertEqual(second.remember("key", "second"), "first")
        second.clear_cache()
        self.assertEqual(first.cache_snapshot(), {})
        self.assertEqual(first.remember("key", "new"), "new")

    def test_invalid_inputs_and_snapshot_ownership(self):
        for bad in [None, "", 1]:
            with self.assertRaises((TypeError, ValueError)):
                with lab.request_context(bad): pass
            with self.assertRaises((TypeError, ValueError)): lab.remember(bad, "value")
            with self.assertRaises((TypeError, ValueError)): lab.remember("key", bad)
        self.assertEqual(lab.cache_snapshot(), {})
        lab.remember("key", "value")
        snapshot = lab.cache_snapshot()
        snapshot["key"] = "changed"
        self.assertEqual(lab.cache_snapshot(), {"key": "value"})


if __name__ == "__main__":
    unittest.main()
