import unittest
from main import make_bonus_rule, run_rule


class ScoreContract(unittest.TestCase):
    def test_normal_zero_and_repeat(self):
        bonus = make_bonus_rule(3)
        self.assertEqual([run_rule(4, bonus), run_rule(0, bonus), run_rule(4, bonus)], [7, 3, 7])
        self.assertEqual(run_rule(4, lambda value: value * 2), 8)

    def test_configurations_are_independent(self):
        first, second = make_bonus_rule(1), make_bonus_rule(9)
        self.assertEqual([first(2), second(2), first(2)], [3, 11, 3])

    def test_exactly_once_and_failure_propagation(self):
        seen = []
        def fail(value):
            seen.append(value)
            raise LookupError("broken rule")
        with self.assertRaisesRegex(LookupError, "broken rule"):
            run_rule(4, fail)
        self.assertEqual(seen, [4])

    def test_input_and_configuration_errors(self):
        for value in [True, "4", None]:
            with self.assertRaises(TypeError): make_bonus_rule(value)
            with self.assertRaises(TypeError): run_rule(value, lambda x: x)
        with self.assertRaises(ValueError): make_bonus_rule(-1)
        with self.assertRaises(ValueError): run_rule(-1, lambda x: x)
        with self.assertRaises(TypeError): run_rule(1, None)

    def test_return_boundary(self):
        for value in [True, "4", None]:
            with self.assertRaises(TypeError): run_rule(1, lambda x: value)
        with self.assertRaises(ValueError): run_rule(1, lambda x: -1)


if __name__ == "__main__": unittest.main()
