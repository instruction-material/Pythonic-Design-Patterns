import unittest
from dataclasses import FrozenInstanceError
import main as lab


class FactoryContracts(unittest.TestCase):
    def test_factories_create_independent_services_and_configs(self):
        first = lab.create_application(lab.Config("A:"))
        second = lab.create_application(lab.Config("B:"))
        self.assertIsNot(first.store, second.store)
        self.assertEqual(first.run(" hello "), "A:hello")
        self.assertEqual(second.run(" hi "), "B:hi")
        self.assertEqual(first.store.messages, ("A:hello",))
        self.assertEqual(second.store.messages, ("B:hi",))
        with self.assertRaises(FrozenInstanceError):
            first.config.prefix = "changed"
        first.close(); second.close()

    def test_injected_factory_once_and_shutdown_once(self):
        calls = []
        class Store:
            def save(self, value): calls.append(("save", value))
            def close(self): calls.append(("close",))
        def factory():
            calls.append(("factory",))
            return Store()
        app = lab.create_application(lab.Config("!"), factory)
        with app:
            self.assertEqual(app.run(" x "), "!x")
        app.close()
        self.assertEqual(calls, [("factory",), ("save", "!x"), ("close",)])
        with self.assertRaises(RuntimeError): app.run("after")
        with self.assertRaises(RuntimeError): app.__enter__()

    def test_body_failure_is_preserved_with_successful_shutdown(self):
        error = RuntimeError("body")
        store = lab.MemoryStore()
        with self.assertRaises(RuntimeError) as caught:
            with lab.create_application(lab.Config("!"), lambda: store):
                raise error
        self.assertIs(caught.exception, error)
        self.assertTrue(store.closed)

    def test_failures_propagate_without_fake_success(self):
        error = OSError("store failed")
        class Store:
            def save(self, value): raise error
            def close(self): pass
        app = lab.create_application(lab.Config("!"), Store)
        with self.assertRaises(OSError) as caught: app.run("x")
        self.assertIs(caught.exception, error)
        app.close()
        def fail(): raise error
        with self.assertRaises(OSError) as caught:
            lab.create_application(lab.Config("!"), fail)
        self.assertIs(caught.exception, error)

    def test_invalid_setup_and_message_have_no_store_effect(self):
        for prefix in [None, ""]:
            with self.assertRaises((TypeError, ValueError)): lab.Config(prefix)
        calls = []
        def factory(): calls.append("created"); return lab.MemoryStore()
        with self.assertRaises(TypeError): lab.create_application(None, factory)
        self.assertEqual(calls, [])
        with self.assertRaises(TypeError): lab.create_application(lab.Config("!"), None)
        with self.assertRaises(TypeError): lab.create_application(lab.Config("!"), lambda: object())
        with lab.create_application(lab.Config("!")) as app:
            with self.assertRaises(TypeError): app.run(None)
            self.assertEqual(app.store.messages, ())


if __name__ == "__main__":
    unittest.main()
