import unittest
from dataclasses import FrozenInstanceError
import main as lab


class ProviderContracts(unittest.TestCase):
    def test_provider_and_fallback_have_exact_ordered_outputs(self):
        rows = [lab.Article("a", "blog", "one"), lab.Article("b", "news", "two"), lab.Article("a", "blog", "one")]
        self.assertEqual(lab.render_document(rows, {"blog": lab.plain}, lab.other), "[BLOG] a: one\n[OTHER] b: two\n[BLOG] a: one")
        self.assertEqual(lab.render_document([], {}, lab.other), "")

    def test_registry_snapshot_and_immutable_values(self):
        providers = {"blog": lab.plain}
        registry = lab.make_registry(providers)
        providers["blog"] = lab.compact
        row = lab.Article("a", "blog", "b")
        self.assertEqual(lab.render_document([row], registry, lab.other), "[BLOG] a: b")
        with self.assertRaises(TypeError): registry["new"] = lab.other
        with self.assertRaises(FrozenInstanceError): row.kind = "news"

    def test_setup_and_data_fail_before_callbacks(self):
        calls = []
        def render(row): calls.append(row); return "rendered"
        for registry in [{"": render}, {" padded ": render}, {1: render}, {"blog": None}]:
            with self.assertRaises((TypeError, ValueError)): lab.make_registry(registry)
        with self.assertRaises(TypeError): lab.render_document([lab.Article("a", "blog", "b"), None], {"blog": render}, render)
        with self.assertRaises(TypeError): lab.render_document([], {}, None)
        with self.assertRaises(TypeError): lab.Article(1, "blog", "b")
        self.assertEqual(calls, [])

    def test_first_callback_error_identity_and_return_type(self):
        error, calls = RuntimeError("renderer failed"), []
        def fail(row): calls.append(row.title); raise error
        with self.assertRaises(RuntimeError) as caught:
            lab.render_document([lab.Article("a", "blog", "b"), lab.Article("later", "blog", "b")], {"blog": fail}, lab.other)
        self.assertIs(caught.exception, error)
        self.assertEqual(calls, ["a"])
        with self.assertRaises(TypeError): lab.render_document([lab.Article("a", "blog", "b")], {"blog": lambda row: 1}, lab.other)

    def test_replacement_changes_only_selected_behavior_and_owns_input(self):
        rows = [lab.Article("a", "blog", "one"), lab.Article("b", "news", "two")]
        def mutate(row): rows.append(lab.Article("later", "blog", "x")); return lab.compact(row)
        self.assertEqual(lab.render_document(rows, {"blog": mutate}, lab.other), "a | one\n[OTHER] b: two")
        self.assertEqual(len(rows), 3)
        before = lab.render_document(rows[:2], {"blog": lab.plain}, lab.other)
        after = lab.render_document(rows[:2], {"blog": lab.compact}, lab.other)
        self.assertEqual(before.splitlines()[1], after.splitlines()[1])


if __name__ == "__main__":
    unittest.main()
