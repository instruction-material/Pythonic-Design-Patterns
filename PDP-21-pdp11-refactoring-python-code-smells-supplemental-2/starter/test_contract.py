import copy
import unittest
import main as lab


class CharacterizationContracts(unittest.TestCase):
    def test_ordinary_and_uppercase_have_exact_preserved_outputs(self):
        rows = [{"title": " Hello ", "kind": "blog", "body": " World "}]
        self.assertEqual(lab.format_refactored(rows), "[BLOG] hello: world")
        self.assertEqual(lab.format_refactored(rows, uppercase=True), "[BLOG] HELLO: WORLD")
        self.assertEqual(lab.format_refactored(rows), lab.format_legacy(rows))

    def test_filter_padded_kinds_and_unknown_kinds_keep_legacy_rules(self):
        cases = [("blog", "[BLOG] hello: world"), ("news", "[NEWS] hello: world"), (" BLOG ", "[OTHER] hello: world"), ("note", "[OTHER] hello: world")]
        for kind, expected in cases:
            rows = [{"title": " Hello ", "kind": kind, "body": " World "}]
            self.assertEqual(lab.format_refactored(rows), expected)
            self.assertEqual(lab.format_refactored(rows, "blog"), expected if kind == "blog" else "")

    def test_empty_duplicates_order_and_input_ownership(self):
        self.assertEqual(lab.format_refactored([]), "")
        rows = [{"title": " B ", "kind": "blog", "body": " two "}, {"title": " A ", "kind": "news", "body": " one "}]
        original = copy.deepcopy(rows)
        self.assertEqual(lab.format_refactored(iter(rows + rows)), "[BLOG] b: two\n[NEWS] a: one\n[BLOG] b: two\n[NEWS] a: one")
        self.assertEqual(rows, original)

    def test_characterized_failure_order_survives_extraction(self):
        for kind_filter, expected in [("all", "title"), ("blog", "kind")]:
            for operation in [lab.format_legacy, lab.format_refactored]:
                with self.assertRaises(KeyError) as caught:
                    operation([{"body": "x"}], kind_filter)
                self.assertEqual(caught.exception.args, (expected,))
        for operation in [lab.format_legacy, lab.format_refactored]:
            self.assertEqual(operation([{"kind": "news"}], "blog"), "")

    def test_capture_records_return_and_error_without_changing_rules(self):
        self.assertEqual(lab.capture_outcome(lambda: "ok"), ("returned", "ok"))
        def fail(): raise KeyError("kind")
        self.assertEqual(lab.capture_outcome(fail), ("raised", "KeyError: 'kind'"))
        rows = [{"body": "x"}]
        self.assertEqual(lab.capture_outcome(lambda: lab.format_legacy(rows, "blog")), lab.capture_outcome(lambda: lab.format_refactored(rows, "blog")))


if __name__ == "__main__":
    unittest.main()
