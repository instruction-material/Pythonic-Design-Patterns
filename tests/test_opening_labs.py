"""Behavioral acceptance for the two repaired opening source families."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
FOLDERS = [
    "PDP-01-pdp1-why-python-changes-the-design-patterns-conversation-supplemental-2",
    "PDP-02-pdp1-why-python-changes-the-design-patterns-conversation-supplemental-3",
]


def load(index, role="solution"):
    name = f"pdp_{index}_{role}"
    spec = importlib.util.spec_from_file_location(
        name, ROOT / FOLDERS[index] / role / "main.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class OpeningContracts(unittest.TestCase):
    def setUp(self):
        self.a = load(0)
        self.b = load(1)

    def test_function_and_whitespace(self):
        self.assertEqual(self.a.title_case("  design patterns  "),
                         "  Design Patterns  ")
        self.assertEqual(self.a.title_case(""), "")
        with self.assertRaises(TypeError):
            self.a.title_case(4)

    def test_closure_and_object_are_interchangeable(self):
        values = ["design patterns", "", "already UPPER", "  spaced  "]
        expected = ["LOG: design patterns", "LOG: ", "LOG: already UPPER",
                    "LOG:   spaced  "]
        for formatter in [self.a.make_prefix_formatter("LOG: "),
                          self.a.PrefixFormatter("LOG: ")]:
            self.assertEqual(self.a.format_messages(values, formatter), expected)
        self.assertEqual(values, ["design patterns", "", "already UPPER",
                                  "  spaced  "])

    def test_configuration_isolation(self):
        a = self.a.make_prefix_formatter("A:")
        b = self.a.make_prefix_formatter("B:")
        self.assertEqual([a("x"), b("x"), a("y")], ["A:x", "B:x", "A:y"])
        self.assertEqual(self.a.PrefixFormatter("")("x"), "x")

    def test_configuration_validation(self):
        for factory in [self.a.make_prefix_formatter, self.a.PrefixFormatter,
                        self.b.make_rulebook]:
            with self.assertRaises(TypeError):
                factory(None)

    def test_driver_order_empty_and_bad_returns(self):
        calls = []
        def recording(text):
            calls.append(text)
            return text.upper()
        self.assertEqual(self.a.format_messages(iter(["b", "a"]), recording),
                         ["B", "A"])
        self.assertEqual(calls, ["b", "a"])
        self.assertEqual(self.a.format_messages([], recording), [])
        with self.assertRaises(TypeError):
            self.a.format_messages(["ok", 2], recording)
        with self.assertRaises(TypeError):
            self.a.format_messages(["ok"], lambda _: 2)

    def test_named_rules(self):
        rules = self.b.make_rulebook("LOG: ")
        self.assertEqual(list(rules), ["title", "prefix", "identity"])
        values = ["design patterns", ""]
        self.assertEqual(self.b.format_named(values, "title", rules),
                         ["Design Patterns", ""])
        self.assertEqual(self.b.format_named(values, "prefix", rules),
                         ["LOG: design patterns", "LOG: "])
        self.assertEqual(self.b.format_named(values, "identity", rules), values)

    def test_named_configuration_and_registry_isolation(self):
        a = self.b.make_rulebook("A:")
        b = self.b.make_rulebook("B:")
        a["extra"] = str.upper
        self.assertNotIn("extra", b)
        self.assertEqual(a["prefix"]("x"), "A:x")
        self.assertEqual(b["prefix"]("x"), "B:x")
        self.assertEqual(self.b.make_rulebook("")["prefix"]("x"), "x")

    def test_custom_rule_needs_no_subclass(self):
        rules = {"reverse": lambda text: text[::-1]}
        self.assertEqual(self.b.format_named(["abc", ""], "reverse", rules),
                         ["cba", ""])
        self.assertEqual(list(rules), ["reverse"])

    def test_missing_choice_fails_even_for_empty_input(self):
        rules = self.b.make_rulebook("")
        with self.assertRaises(ValueError) as caught:
            self.b.format_named([], "missing", rules)
        self.assertIsInstance(caught.exception.__cause__, KeyError)
        self.assertEqual(list(rules), ["title", "prefix", "identity"])

    def test_bad_rule_inputs_and_returns(self):
        for action in [
            lambda: self.b.select_formatter(None, {}),
            lambda: self.b.select_formatter("bad", {"bad": 4}),
            lambda: self.b.format_named([4], "identity",
                                        self.b.make_rulebook("")),
            lambda: self.b.format_named(["ok"], "bad", {"bad": lambda _: 4}),
        ]:
            with self.assertRaises(TypeError):
                action()

    def test_starters_require_the_declared_work(self):
        for index, actions in [
            (0, [lambda m: m.title_case("x"),
                 lambda m: m.make_prefix_formatter(""),
                 lambda m: m.PrefixFormatter("")("x")]),
            (1, [lambda m: m.make_rulebook(""),
                 lambda m: m.select_formatter("identity", {})]),
        ]:
            module = load(index, "starter")
            for action in actions:
                with self.assertRaises(NotImplementedError):
                    action(module)
            result = subprocess.run(
                [sys.executable, "-B", str(ROOT / FOLDERS[index] /
                                          "starter/main.py")],
                check=True, capture_output=True, text=True, timeout=10)
            self.assertIn("starter unfinished:", result.stdout)

    def test_complete_reference_cli(self):
        outputs = [
            "function: ['Design Patterns', '']\n"
            "closure: ['LOG: design patterns', 'LOG: ']\n"
            "object: ['LOG: design patterns', 'LOG: ']\n",
            "title: ['Design Patterns', '']\n"
            "prefix: ['LOG: design patterns', 'LOG: ']\n"
            "identity: ['design patterns', '']\n",
        ]
        for index, expected in enumerate(outputs):
            result = subprocess.run(
                [sys.executable, "-B", str(ROOT / FOLDERS[index] /
                                          "solution/main.py")],
                check=True, capture_output=True, text=True, timeout=10)
            self.assertEqual(result.stdout, expected)
            self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
