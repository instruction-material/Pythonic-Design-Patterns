import unittest
from main import Registry, deliver

class LifetimeContracts(unittest.TestCase):
    def test_owned_handle_closes_idempotently(self):
        registry, seen = Registry(), []
        handle = registry.connect(seen.append)
        deliver(registry, "ready")
        handle.close()
        handle.close()
        deliver(registry, "later")
        self.assertEqual(seen, ["ready"])
        self.assertEqual(registry.listeners, {})

    def test_context_disconnects_after_success_and_failure(self):
        registry, seen, failure = Registry(), [], LookupError("body")
        with registry.connect(seen.append): deliver(registry, "")
        with self.assertRaises(LookupError) as caught:
            with registry.connect(seen.append):
                deliver(registry, "inside")
                raise failure
        self.assertIs(caught.exception, failure)
        deliver(registry, "after")
        self.assertEqual(seen, ["", "inside"])
        self.assertEqual(registry.listeners, {})

    def test_duplicate_connections_are_independent_and_closed_handle_stays_closed(self):
        registry, seen = Registry(), []
        first, second = registry.connect(seen.append), registry.connect(seen.append)
        self.assertNotEqual(first.token, second.token)
        first.close()
        with first: deliver(registry, "once")
        self.assertEqual(seen, ["once"])
        second.close()
        deliver(registry, "never")
        self.assertEqual(seen, ["once"])

    def test_disconnect_during_delivery_keeps_captured_callback(self):
        registry, seen = Registry(), []
        def first(value):
            seen.append("first")
            second.close()
        registry.connect(first)
        second = registry.connect(lambda value: seen.append("second"))
        deliver(registry, "ready")
        deliver(registry, "later")
        self.assertEqual(seen, ["first", "second", "first"])

    def test_failures_and_invalid_inputs_have_no_retry(self):
        registry, seen, failure = Registry(), [], OSError("callback")
        def fail(value):
            seen.append(value)
            raise failure
        handle = registry.connect(fail)
        registry.connect(lambda value: seen.append("later"))
        with self.assertRaises(OSError) as caught: deliver(registry, "ready")
        self.assertIs(caught.exception, failure)
        self.assertEqual(seen, ["ready"])
        handle.close()
        with self.assertRaises(TypeError): deliver(registry, None)
        with self.assertRaises(TypeError): registry.connect(None)
        invalid = Registry()
        invalid.connect(lambda value: 4)
        with self.assertRaises(TypeError): deliver(invalid, "ready")

if __name__ == "__main__": unittest.main()
