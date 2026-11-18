from dataclasses import FrozenInstanceError
import unittest
from main import Config, add_section, render_text


class ConstructionContract(unittest.TestCase):
    def test_order_and_original_preserved(self):
        base = Config("Plan")
        first = add_section(base, "draft")
        second = add_section(first, "reviewed")
        self.assertEqual(base.sections, ())
        self.assertEqual(first.sections, ("draft",))
        self.assertEqual(second.sections, ("draft", "reviewed"))
        self.assertIsNot(base, first)
        self.assertEqual(render_text(second), "PLAN\ndraft\nreviewed")

    def test_empty_sections_and_footer(self):
        self.assertEqual(render_text(Config("Plan")), "PLAN")
        self.assertEqual(render_text(Config("Plan", footer=True)), "PLAN\n-- end --")

    def test_frozen_values_and_exact_text(self):
        base = Config(" Plan ")
        with self.assertRaises(FrozenInstanceError): base.title = "other"
        self.assertEqual(add_section(base, " draft ").sections, (" draft ",))
        self.assertEqual(render_text(base), " PLAN ")

    def test_construction_errors(self):
        for value in [None, 3, True]:
            with self.assertRaises(TypeError): Config(value)
        with self.assertRaises(ValueError): Config(" ")
        with self.assertRaises(TypeError): Config("Plan", [])
        with self.assertRaises(ValueError): Config("Plan", (" ",))
        with self.assertRaises(TypeError): Config("Plan", footer=1)

    def test_call_boundaries(self):
        with self.assertRaises(TypeError): add_section(None, "ok")
        with self.assertRaises(TypeError): render_text(None)
        with self.assertRaises(ValueError): add_section(Config("Plan"), " ")
        with self.assertRaises(TypeError): add_section(Config("Plan"), None)


if __name__ == "__main__": unittest.main()
