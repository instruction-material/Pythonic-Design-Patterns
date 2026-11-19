import unittest
import main as lab


class PipelineContracts(unittest.TestCase):
    def test_hook_callable_equivalence_and_identity(self):
        values = [1, -2, 1]
        self.assertEqual(lab.run_steps(values, lab.compose_stages(lambda n: n + 1, lambda n: n * 2)), [4, -2, 4])
        self.assertEqual(lab.AddThenDouble().run(values), [4, -2, 4])
        self.assertEqual(lab.run_steps(values, lab.compose_stages()), values)
        self.assertEqual(lab.run_steps([], lab.compose_stages()), [])

    def test_stage_order_and_owned_input(self):
        values = [1, 2]
        calls = []
        def first(value):
            calls.append(("first", value))
            values.append(99)
            return value + 1
        def second(value):
            calls.append(("second", value))
            return value * 2
        self.assertEqual(lab.run_steps(values, lab.compose_stages(first, second)), [4, 6])
        self.assertEqual(calls, [("first", 1), ("second", 2), ("first", 2), ("second", 3)])

    def test_first_error_keeps_identity_and_stops(self):
        error = RuntimeError("stage failed")
        calls = []
        def fail(value):
            calls.append(value)
            raise error
        with self.assertRaises(RuntimeError) as caught:
            lab.run_steps([1, 2], lab.compose_stages(fail, lambda n: calls.append("later")))
        self.assertIs(caught.exception, error)
        self.assertEqual(calls, [1])

    def test_setup_and_inputs_validated_before_invocation(self):
        calls = []
        with self.assertRaises(TypeError):
            lab.compose_stages(None)
        with self.assertRaises(TypeError):
            lab.run_steps([1, True], lambda n: calls.append(n))
        self.assertEqual(calls, [])
        with self.assertRaises(TypeError):
            lab.run_steps([], None)

    def test_stage_return_boundary_and_generator_input(self):
        for bad in [True, "2", None]:
            with self.subTest(bad=bad), self.assertRaises(TypeError):
                lab.run_steps([1], lab.compose_stages(lambda n: bad))
        self.assertEqual(lab.run_steps((n for n in [3, 4]), lab.compose_stages(lambda n: n - 1)), [2, 3])


if __name__ == "__main__":
    unittest.main()
