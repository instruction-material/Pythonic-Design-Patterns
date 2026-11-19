import unittest
import main as lab


class DependencyContracts(unittest.TestCase):
    def test_static_internal_imports_aliases_and_external_modules(self):
        sources = {"app": "import model as m\nfrom model import Thing\nimport json\nif False:\n import render", "model": "", "render": "from model import Thing"}
        self.assertEqual(lab.dependency_map(sources), {"app": ("model", "render"), "model": (), "render": ("model",)})
        self.assertIn("import model", sources["app"])

    def test_source_is_never_executed_and_graph_is_owned(self):
        sources = {"a": "raise RuntimeError('never execute')", "b": "import a"}
        graph = lab.dependency_map(sources)
        self.assertEqual(graph, {"a": (), "b": ("a",)})
        sources["b"] = ""
        self.assertEqual(graph["b"], ("a",))
        self.assertEqual(lab.dependency_map({}), {})

    def test_transitive_dependents_and_cycles_terminate(self):
        graph = {"a": ["b"], "b": ["c"], "c": ["a"], "other": []}
        self.assertEqual(lab.affected_modules(graph, "c"), ("a", "b", "c"))
        self.assertEqual(lab.affected_modules(graph, "other"), ("other",))
        self.assertEqual(graph["a"], ["b"])
        self.assertEqual(lab.affected_modules({"a": iter(["b"]), "b": []}, "b"), ("a", "b"))

    def test_syntax_and_unsupported_layout_fail_explicitly(self):
        with self.assertRaises(SyntaxError) as caught: lab.dependency_map({"app": "def broken("})
        self.assertEqual(caught.exception.filename, "app.py")
        with self.assertRaises(ValueError): lab.dependency_map({"app": "from . import model", "model": ""})
        for name in ["not a module", "a.b", "class"]:
            with self.assertRaises(ValueError): lab.dependency_map({name: ""})
        with self.assertRaises(TypeError): lab.dependency_map({"app": None})

    def test_missing_and_invalid_dependency_boundaries(self):
        with self.assertRaises(KeyError) as caught: lab.affected_modules({"a": []}, "missing")
        self.assertEqual(caught.exception.args, ("missing",))
        with self.assertRaises(ValueError): lab.affected_modules({"a": ["missing"]}, "a")
        with self.assertRaises(TypeError): lab.affected_modules({"a": [True]}, "a")
        with self.assertRaises(ValueError): lab.affected_modules({"a": ["a"]}, "not valid")


if __name__ == "__main__":
    unittest.main()
