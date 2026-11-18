"""Learner contract: independent mutable records and copied snapshots."""
import unittest
from main import TaskRecord, new_task, snapshot_task


class RecordContract(unittest.TestCase):
    def test_new_task_preserves_order_values_and_owns_input(self):
        tags = ["b", "a", "b"]
        record = new_task(" plan ", tags)
        self.assertEqual(record.name, " plan ")
        self.assertEqual(record.tags, ["b", "a", "b"])
        tags.append("caller")
        self.assertEqual(record.tags, ["b", "a", "b"])
        seen = []
        def values():
            for tag in ["new", "ready"]:
                seen.append(tag)
                yield tag
        self.assertEqual(new_task("one pass", values()).tags, ["new", "ready"])
        self.assertEqual(seen, ["new", "ready"])

    def test_default_lists_are_independent(self):
        first, second = new_task("first"), new_task("second")
        first.tags.append("new")
        self.assertEqual(second.tags, [])
        direct_a, direct_b = TaskRecord("a"), TaskRecord("b")
        direct_a.tags.append("only a")
        self.assertEqual(direct_b.tags, [])

    def test_snapshot_is_independent_in_both_directions(self):
        record = new_task("plan", ["new"])
        snapshot = snapshot_task(record)
        self.assertEqual(snapshot, {"name": "plan", "tags": ["new"]})
        record.tags.append("live")
        self.assertEqual(snapshot["tags"], ["new"])
        snapshot["tags"].append("saved")
        snapshot["name"] = "copy"
        self.assertEqual(record.tags, ["new", "live"])
        self.assertEqual(record.name, "plan")

    def test_invalid_creation_values(self):
        for name in ["", "   "]:
            with self.assertRaises(ValueError):
                new_task(name)
        for name in [4, None]:
            with self.assertRaises(TypeError):
                new_task(name)
        for tags in ["new", b"new", None, [4]]:
            with self.assertRaises(TypeError):
                new_task("plan", tags)
        for tags in [[""], [" "]]:
            with self.assertRaises(ValueError):
                new_task("plan", tags)

    def test_snapshot_checks_current_mutable_state(self):
        for value in [object(), None]:
            with self.assertRaises(TypeError):
                snapshot_task(value)
        record = new_task("plan")
        record.tags.append(4)
        with self.assertRaises(TypeError):
            snapshot_task(record)
        record.tags = ()
        with self.assertRaises(TypeError):
            snapshot_task(record)
        record.tags = []
        record.name = ""
        with self.assertRaises(ValueError):
            snapshot_task(record)


if __name__ == "__main__":
    unittest.main()
