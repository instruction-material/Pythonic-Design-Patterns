import unittest
from main import Event, publish_snapshot, subscribe

class SnapshotContracts(unittest.TestCase):
    def test_empty_normal_and_duplicate_listeners(self):
        listeners, seen = [], []
        publish_snapshot(listeners, Event("order", 0))
        def receive(event): seen.append((event.topic, event.value))
        subscribe(listeners, receive)
        subscribe(listeners, receive)
        publish_snapshot(listeners, Event("order", 3))
        self.assertEqual(seen, [("order", 3), ("order", 3)])

    def test_mutation_during_delivery_uses_the_original_snapshot(self):
        listeners, seen, changed = [], [], []
        def later(event): seen.append("later")
        def first(event):
            seen.append("first")
            if not changed:
                listeners.remove(second)
                subscribe(listeners, later)
                changed.append(True)
        def second(event): seen.append("second")
        subscribe(listeners, first)
        subscribe(listeners, second)
        publish_snapshot(listeners, Event("order", 1))
        self.assertEqual(seen, ["first", "second"])
        seen.clear()
        publish_snapshot(listeners, Event("order", 2))
        self.assertEqual(seen, ["first", "later"])

    def test_original_exception_stops_later_delivery(self):
        listeners, seen, failure = [], [], OSError("failed")
        def fail(event):
            seen.append("failed")
            raise failure
        subscribe(listeners, fail)
        subscribe(listeners, lambda event: seen.append("later"))
        with self.assertRaises(OSError) as caught:
            publish_snapshot(listeners, Event("order", 1))
        self.assertIs(caught.exception, failure)
        self.assertEqual(seen, ["failed"])

    def test_invalid_values_are_rejected_without_partial_delivery(self):
        listeners, seen = [], []
        with self.assertRaises(TypeError): subscribe(listeners, None)
        self.assertEqual(listeners, [])
        for value in [True, "3", None]:
            with self.assertRaises(TypeError): Event("order", value)
        with self.assertRaises(ValueError): Event("order", -1)
        with self.assertRaises(ValueError): Event(" ", 3)
        with self.assertRaises(TypeError): Event(4, 3)
        listeners[:] = [lambda event: seen.append("first"), None]
        with self.assertRaises(TypeError): publish_snapshot(listeners, Event("order", 3))
        self.assertEqual(seen, [])

    def test_payload_is_immutable_and_callback_result_has_a_contract(self):
        from dataclasses import FrozenInstanceError
        event = Event("order", 3)
        with self.assertRaises(FrozenInstanceError): event.value = 9
        with self.assertRaises(TypeError): publish_snapshot([], {})
        with self.assertRaises(TypeError): publish_snapshot([lambda event: 1], event)

if __name__ == "__main__": unittest.main()
