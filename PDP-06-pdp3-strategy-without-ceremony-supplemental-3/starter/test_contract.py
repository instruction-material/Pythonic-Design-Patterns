import unittest
from main import choose_best, register_score_rule


class SelectionContract(unittest.TestCase):
    def test_winner_and_insertion_order_ties(self):
        rules = {"first": lambda value: value + 1, "second": lambda value: value + 1}
        self.assertEqual(choose_best(0, rules), ("first", 1))
        self.assertEqual(choose_best(4, {"double": lambda x: x * 2, "bonus": lambda x: x + 5}), ("bonus", 9))

    def test_one_call_each_and_binding_snapshot(self):
        seen = []
        rules = {}
        def first(value):
            seen.append("first")
            rules.clear()
            return value
        def second(value):
            seen.append("second")
            return value + 1
        rules.update(first=first, second=second)
        self.assertEqual(choose_best(2, rules), ("second", 3))
        self.assertEqual(seen, ["first", "second"])

    def test_registration_rejects_before_mutation(self):
        rules = {}
        rule = lambda value: value
        register_score_rule(rules, "same", rule)
        with self.assertRaises(ValueError): register_score_rule(rules, "same", lambda value: 0)
        with self.assertRaises(ValueError): register_score_rule(rules, " ", rule)
        with self.assertRaises(TypeError): register_score_rule(rules, "new", None)
        self.assertEqual(rules, {"same": rule})

    def test_empty_and_invalid_inputs(self):
        with self.assertRaises(ValueError): choose_best(0, {})
        with self.assertRaises(TypeError): choose_best(True, {"ok": lambda x: x})
        with self.assertRaises(ValueError): choose_best(-1, {"ok": lambda x: x})
        with self.assertRaises(ValueError): choose_best(1, {" ": lambda x: x})
        with self.assertRaises(TypeError): choose_best(1, {"bad": None})
        with self.assertRaises(TypeError): choose_best(1, {"bad": lambda x: True})
        with self.assertRaises(ValueError): choose_best(1, {"bad": lambda x: -1})

    def test_error_stops_later_rules(self):
        seen = []
        def fail(value):
            seen.append("fail")
            raise LookupError("no retry")
        def later(value):
            seen.append("later")
            return value
        with self.assertRaisesRegex(LookupError, "no retry"):
            choose_best(1, {"fail": fail, "later": later})
        self.assertEqual(seen, ["fail"])


if __name__ == "__main__": unittest.main()
