import unittest
from main import make_increment, run_queue

class Contracts(unittest.TestCase):
    def test_configuration_is_captured_and_independent(self):
        config = {"amount": 3}; a = make_increment(config)
        config["amount"] = 10; b = make_increment(config)
        self.assertEqual([a(2), b(2), a(4)], [5, 12, 7])
    def test_empty_ordered_queue_and_negative_values(self):
        self.assertEqual(run_queue(-2, []), -2)
        self.assertEqual(run_queue(2, [lambda n: n * 3, make_increment({"amount": -1})]), 5)
    def test_queue_membership_is_captured_before_execution(self):
        actions = []
        def first(value):
            actions.clear(); actions.append(lambda n: n + 100)
            return value + 1
        actions.extend([first, lambda n: n * 2])
        self.assertEqual(run_queue(2, actions), 6)
    def test_invalid_entries_are_rejected_before_callbacks(self):
        seen = []
        with self.assertRaises(TypeError): run_queue(0, [lambda n: seen.append(n), None])
        self.assertEqual(seen, [])
        for value in [True, 1.5, "3"]:
            with self.assertRaises(TypeError): make_increment({"amount": value})
            with self.assertRaises(TypeError): run_queue(value, [])
    def test_exception_identity_and_invalid_result(self):
        error = LookupError("first")
        def fail(n): raise error
        with self.assertRaises(LookupError) as caught: run_queue(2, [fail])
        self.assertIs(caught.exception, error)
        with self.assertRaises(TypeError): run_queue(2, [lambda n: True])

if __name__ == "__main__": unittest.main()
