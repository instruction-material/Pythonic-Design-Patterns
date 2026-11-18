"""Public transparency, caching, authorization and facade contracts."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stdout
import gc
import inspect
from io import StringIO
from threading import Event
import unittest
import warnings
from main import (AuthorizationProxy, ProfileFacade, ProfileService, cache_result,
                  clear_cache, log_calls)


class ValueAndGeneratorContracts(unittest.TestCase):
    def test_metadata_arguments_return_and_original_failure(self):
        result, failure = object(), LookupError("core")
        def operation(value: int, *, fail: bool = False) -> object:
            """The core operation."""
            if fail: raise failure
            self.assertEqual(value, 4)
            return result
        wrapped = log_calls(operation)
        self.assertEqual(inspect.signature(wrapped), inspect.signature(operation))
        for field in ["__name__", "__doc__", "__annotations__"]:
            self.assertEqual(getattr(wrapped, field), getattr(operation, field))
        self.assertIs(wrapped.__wrapped__, operation)
        with redirect_stdout(StringIO()):
            self.assertIs(wrapped(4, fail=False), result)
            with self.assertRaises(LookupError) as caught: wrapped(4, fail=True)
        self.assertIs(caught.exception, failure)
        self.assertIs(wrapped.__wrapped__(4), result)

    def test_decorator_order_changes_observed_logging_not_value(self):
        first_calls, second_calls = [], []
        def first(value=4):
            first_calls.append(value)
            return value
        def second(value=4):
            second_calls.append(value)
            return value
        cache_outside = cache_result(log_calls(first))
        log_outside = log_calls(cache_result(second))
        first_log, second_log = StringIO(), StringIO()
        with redirect_stdout(first_log):
            self.assertEqual(cache_outside(), 4)
            self.assertEqual(cache_outside(value=4), 4)
        with redirect_stdout(second_log):
            self.assertEqual(log_outside(), 4)
            self.assertEqual(log_outside(value=4), 4)
        self.assertEqual(first_calls, [4])
        self.assertEqual(second_calls, [4])
        self.assertEqual(first_log.getvalue().count("log: calling"), 1)
        self.assertEqual(second_log.getvalue().count("log: calling"), 2)

    def test_normalized_keys_defaults_var_keywords_hashability_and_identity(self):
        calls = []
        def operation(value=4, *, multiplier=2, **options):
            calls.append((value, multiplier, dict(options)))
            return {"value": value * multiplier, "options": options}
        wrapped = cache_result(operation)
        first = wrapped(4, x=1, y=2)
        self.assertIs(wrapped(value=4, multiplier=2, y=2, x=1), first)
        self.assertEqual(len(calls), 1)
        self.assertEqual(wrapped()["value"], 8)
        with self.assertRaises(TypeError): wrapped([])
        with self.assertRaises(TypeError): wrapped(4, 2)
        self.assertEqual(len(calls), 2)

    def test_exceptions_are_not_cached_and_clear_invalidates_results(self):
        calls, failure = [], OSError("first")
        def operation(value):
            calls.append(value)
            if len(calls) == 1: raise failure
            return object()
        wrapped = cache_result(operation)
        with self.assertRaises(OSError) as caught: wrapped(4)
        self.assertIs(caught.exception, failure)
        first = wrapped(4)
        self.assertIs(wrapped(value=4), first)
        clear_cache(wrapped)
        self.assertIsNot(wrapped(4), first)
        self.assertEqual(calls, [4, 4, 4])
        with self.assertRaises(TypeError): clear_cache(operation)

    def test_simultaneous_misses_compute_once_under_the_reentrant_lock(self):
        entered, release, calls = Event(), Event(), []
        result = object()
        def operation(value):
            calls.append(value)
            entered.set()
            if not release.wait(3): raise RuntimeError("release timed out")
            return result
        wrapped = cache_result(operation)
        with ThreadPoolExecutor(max_workers=2) as pool:
            first = pool.submit(wrapped, 4)
            try:
                self.assertTrue(entered.wait(2))
                second = pool.submit(wrapped, value=4)
            finally:
                release.set()
            self.assertIs(first.result(timeout=3), result)
            self.assertIs(second.result(timeout=3), result)
        self.assertEqual(calls, [4])

    def test_proxy_owns_snapshots_and_rechecks_policy_before_cache_hits(self):
        class Service:
            def __init__(self):
                self.loads = 0
                self.raw = {"username": "ada", "plan": "pro", "status": "active"}
            def get_profile(self, username):
                self.loads += 1
                return self.raw
        service, allowed = Service(), {"ada"}
        proxy = AuthorizationProxy(service, allowed)
        allowed.add("bob")
        with self.assertRaises(PermissionError): proxy.get_profile("bob")
        first = proxy.get_profile("ada")
        first["plan"] = "caller edit"
        service.raw["plan"] = "new core"
        self.assertEqual(proxy.get_profile("ada")["plan"], "pro")
        self.assertEqual(service.loads, 1)
        proxy.allowed_users.remove("ada")
        with self.assertRaises(PermissionError): proxy.get_profile("ada")
        self.assertEqual(service.loads, 1)
        proxy.allowed_users.add("ada")
        proxy.invalidate()
        self.assertEqual(proxy.get_profile("ada")["plan"], "new core")
        self.assertEqual(service.loads, 2)

    def test_facade_orders_conforming_services_and_skips_billing_after_denial(self):
        seen = []
        class Profiles:
            def get_profile(self, username):
                seen.append("profile:" + username)
                if username == "blocked": raise PermissionError("denied")
                return {"username": username, "plan": "pro", "status": "active"}
        class Billing:
            def get_balance(self, username):
                seen.append("billing:" + username)
                return "paid"
        facade = ProfileFacade(Profiles(), Billing())
        self.assertEqual(facade.load_dashboard("ada"), "ada -> plan=pro status=active billing=paid")
        self.assertEqual(seen, ["profile:ada", "billing:ada"])
        seen.clear()
        with self.assertRaises(PermissionError): facade.load_dashboard("blocked")
        self.assertEqual(seen, ["profile:blocked"])
        self.assertEqual(ProfileFacade(Profiles()).load_dashboard("ada"),
                         "ada -> plan=pro status=active billing=paid")
        with redirect_stdout(StringIO()):
            service = ProfileService()
            proxy = AuthorizationProxy(service, {"ada"})
            proxy.get_profile("ada")
            proxy.get_profile(username="ada")
        self.assertEqual(service.loads, 1)
        for invalid in [None, True]:
            with self.assertRaises(TypeError): proxy.get_profile(invalid)
        with self.assertRaises(ValueError): proxy.get_profile(" ")

    def test_generator_send_throw_return_and_close_are_delegated(self):
        cleanup = []
        def stream(seed):
            try:
                value = yield seed
                try: yield value
                except LookupError: yield "recovered"
                return "done"
            finally: cleanup.append("closed")
        wrapped = log_calls(stream)
        self.assertTrue(inspect.isgeneratorfunction(wrapped))
        self.assertIs(wrapped.__wrapped__, stream)
        with redirect_stdout(StringIO()):
            generator = wrapped(2)
            self.assertEqual(next(generator), 2)
            self.assertEqual(generator.send(5), 5)
            self.assertEqual(generator.throw(LookupError("recover")), "recovered")
            with self.assertRaises(StopIteration) as stopped: next(generator)
            self.assertEqual(stopped.exception.value, "done")
            other = wrapped(3)
            next(other)
            other.close()
        self.assertEqual(cleanup, ["closed", "closed"])


class CoroutineAndAsyncGeneratorContracts(unittest.IsolatedAsyncioTestCase):
    async def test_coroutine_shape_keywords_metadata_result_and_failure(self):
        failure = LookupError("async core")
        async def operation(value: int, *, offset: int = 1) -> int:
            """Async core."""
            await asyncio.sleep(0)
            if value < 0: raise failure
            return value + offset
        wrapped = log_calls(operation)
        self.assertTrue(inspect.iscoroutinefunction(wrapped))
        self.assertEqual(inspect.signature(wrapped), inspect.signature(operation))
        self.assertEqual(wrapped.__annotations__, operation.__annotations__)
        self.assertIs(wrapped.__wrapped__, operation)
        with redirect_stdout(StringIO()):
            self.assertEqual(await wrapped(4, offset=3), 7)
            with self.assertRaises(LookupError) as caught: await wrapped(-1)
        self.assertIs(caught.exception, failure)
        self.assertEqual(await wrapped.__wrapped__(4), 5)

    async def test_async_generator_asend_athrow_completion_and_aclose(self):
        cleanup = []
        async def stream(seed):
            try:
                value = yield seed
                try: yield value
                except LookupError: yield "recovered"
            finally: cleanup.append("closed")
        wrapped = log_calls(stream)
        self.assertTrue(inspect.isasyncgenfunction(wrapped))
        self.assertIs(wrapped.__wrapped__, stream)
        with redirect_stdout(StringIO()):
            generator = wrapped(2)
            self.assertEqual(await generator.__anext__(), 2)
            self.assertEqual(await generator.asend(5), 5)
            self.assertEqual(await generator.athrow(LookupError("recover")), "recovered")
            with self.assertRaises(StopAsyncIteration): await generator.__anext__()
            other = wrapped(3)
            await other.__anext__()
            await other.aclose()
        self.assertEqual(cleanup, ["closed", "closed"])

    async def test_async_generator_cancellation_runs_owned_cleanup(self):
        cleanup, started, release = [], asyncio.Event(), asyncio.Event()
        async def stream():
            try:
                started.set()
                await release.wait()
                yield 1
            finally: cleanup.append("closed")
        wrapped = log_calls(stream)
        with redirect_stdout(StringIO()):
            generator = wrapped()
            task = asyncio.create_task(generator.__anext__())
            try:
                await asyncio.wait_for(started.wait(), 2)
            finally:
                task.cancel()
                with self.assertRaises(asyncio.CancelledError): await task
                await generator.aclose()
        self.assertEqual(cleanup, ["closed"])

    async def test_value_cache_rejects_deferred_function_shapes_and_coroutines(self):
        async def asynchronous(): return 1
        def generator(): yield 1
        async def asynchronous_generator(): yield 1
        for operation in [asynchronous, generator, asynchronous_generator]:
            with self.assertRaises(TypeError): cache_result(operation)
        def dynamic(): return asynchronous()
        with warnings.catch_warnings(record=True) as recorded:
            warnings.simplefilter("always")
            wrapped = cache_result(dynamic)
            with self.assertRaises(TypeError): wrapped()
            gc.collect()
        self.assertFalse([w for w in recorded if issubclass(w.category, RuntimeWarning)])


if __name__ == "__main__":
    unittest.main()
