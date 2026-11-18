"""Complete only declared bodies, then check the untouched learner drivers."""
import ast
import copy
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CASES = [
    ("PDP-03-pdp2-design-foundations-in-python-supplemental-2",
     {"render_notice", "deliver_notice"}),
    ("PDP-04-pdp2-design-foundations-in-python-supplemental-3",
     {"new_task", "snapshot_task"}),
    ("PDP-01-pdp1-why-python-changes-the-design-patterns-conversation-supplemental-2",
     {"title_case", "make_prefix_formatter", "__call__"}),
    ("PDP-02-pdp1-why-python-changes-the-design-patterns-conversation-supplemental-3",
     {"make_rulebook", "select_formatter"}),
]


class CompletedScaffolds(unittest.TestCase):
    def test_only_declared_bodies_complete_each_supplied_driver(self):
        for folder, names in CASES:
            with self.subTest(folder=folder), tempfile.TemporaryDirectory() as tmp:
                starter = ast.parse((ROOT / folder / "starter/main.py").read_text())
                reference = ast.parse((ROOT / folder / "solution/main.py").read_text())
                bodies = {n.name: n.body for n in ast.walk(reference)
                          if isinstance(n, ast.FunctionDef) and n.name in names}
                for node in ast.walk(starter):
                    if isinstance(node, ast.FunctionDef) and node.name in bodies:
                        node.body = copy.deepcopy(bodies[node.name])
                ast.fix_missing_locations(starter)
                Path(tmp, "main.py").write_text(ast.unparse(starter) + "\n")
                shutil.copyfile(ROOT / folder / "starter/test_contract.py",
                                Path(tmp, "test_contract.py"))
                result = subprocess.run(
                    [sys.executable, "-B", "-m", "unittest", "discover",
                     "-s", tmp, "-p", "test_contract.py", "-v"],
                    capture_output=True, text=True, timeout=20)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("Ran 5 tests", result.stderr)


if __name__ == "__main__":
    unittest.main()
