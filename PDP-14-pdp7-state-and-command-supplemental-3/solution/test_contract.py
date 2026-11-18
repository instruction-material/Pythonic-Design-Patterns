import unittest
from main import Document, apply_edit, undo_edit

class Contracts(unittest.TestCase):
    def test_lifo_and_empty(self):
        doc = Document("a"); self.assertFalse(undo_edit(doc))
        apply_edit(doc, "b"); apply_edit(doc, "c")
        self.assertTrue(undo_edit(doc)); self.assertEqual(doc.text, "b")
        self.assertTrue(undo_edit(doc)); self.assertEqual(doc.text, "a")
        self.assertFalse(undo_edit(doc))
    def test_bounded_history_has_a_defined_oldest_state(self):
        doc = Document("zero", limit=2)
        for value in ["one", "two", "three"]: apply_edit(doc, value)
        self.assertEqual(doc.history, ("one", "two"))
        undo_edit(doc); undo_edit(doc)
        self.assertEqual(doc.text, "one"); self.assertFalse(undo_edit(doc))
    def test_repeated_empty_edits_are_owned_entries(self):
        doc = Document("x"); apply_edit(doc, ""); apply_edit(doc, "")
        self.assertEqual(doc.history, ("x", "")); undo_edit(doc)
        self.assertEqual(doc.text, ""); undo_edit(doc); self.assertEqual(doc.text, "x")
    def test_document_histories_do_not_alias(self):
        a, b = Document("a"), Document("b")
        apply_edit(a, "changed"); self.assertEqual(b.history, ())
        captured = a.history; undo_edit(a); self.assertEqual(captured, ("a",))
    def test_invalid_edit_is_atomic_and_configuration_is_checked(self):
        doc = Document("a")
        with self.assertRaises(TypeError): apply_edit(doc, None)
        self.assertEqual((doc.text, doc.history), ("a", ()))
        for value in [True, 1.2, "2"]:
            with self.assertRaises(TypeError): Document(limit=value)
        with self.assertRaises(ValueError): Document(limit=0)

if __name__ == "__main__": unittest.main()
