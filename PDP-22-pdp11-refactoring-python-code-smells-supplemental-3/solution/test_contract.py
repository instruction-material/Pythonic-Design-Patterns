import unittest
import main as lab


class SideEffectContracts(unittest.TestCase):
    def test_normalization_is_pure_ordered_and_retains_duplicates(self):
        rows = [" b ", " ", " a ", " b "]
        self.assertEqual(lab.normalize_rows(rows), ("b", "a", "b"))
        self.assertEqual(rows, [" b ", " ", " a ", " b "])
        self.assertEqual(lab.normalize_rows([]), ())

    def test_writes_follow_prepared_order_and_return_completed_count(self):
        writes = []
        self.assertEqual(lab.publish_rows([" b ", "", " a "], writes.append), 2)
        self.assertEqual(writes, ["b", "a"])
        self.assertEqual(lab.publish_rows([], writes.append), 0)
        self.assertEqual(writes, ["b", "a"])

    def test_invalid_input_produces_no_external_writes(self):
        writes = []
        with self.assertRaises(TypeError): lab.publish_rows(["first", None], writes.append)
        self.assertEqual(writes, [])
        with self.assertRaises(TypeError): lab.publish_rows([], None)

    def test_write_failure_preserves_identity_and_prior_effects(self):
        error = OSError("write failed")
        writes = []
        def write(row):
            if row == "bad": raise error
            writes.append(row)
        with self.assertRaises(OSError) as caught:
            lab.publish_rows(["ok", "bad", "never"], write)
        self.assertIs(caught.exception, error)
        self.assertEqual(writes, ["ok"])

    def test_iterator_failure_and_callback_mutation_have_explicit_boundaries(self):
        error = RuntimeError("source failed")
        writes = []
        def source():
            yield "first"
            raise error
        with self.assertRaises(RuntimeError) as caught: lab.publish_rows(source(), writes.append)
        self.assertIs(caught.exception, error)
        self.assertEqual(writes, [])
        rows = ["a", "b"]
        def write(row):
            writes.append(row)
            rows.append("later")
        self.assertEqual(lab.publish_rows(rows, write), 2)
        self.assertEqual(writes, ["a", "b"])


if __name__ == "__main__":
    unittest.main()
