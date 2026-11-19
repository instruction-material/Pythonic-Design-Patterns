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
    ('PDP-17-pdp9-template-method-versus-higher-order-functions-supplemental-2', {'run_steps', 'compose_stages'}),
    ('PDP-18-pdp9-template-method-versus-higher-order-functions-supplemental-3', {'managed_values', 'take_values'}),
    ('PDP-19-pdp10-singleton-global-state-and-module-patterns', {'run', 'create_application'}),
    ('PDP-20-pdp10-singleton-global-state-and-module-patterns', {'request_context', 'remember'}),
    ('PDP-21-pdp11-refactoring-python-code-smells-supplemental-2', {'format_refactored', 'capture_outcome'}),
    ('PDP-22-pdp11-refactoring-python-code-smells-supplemental-3', {'normalize_rows', 'publish_rows'}),
    ('PDP-23-pdp12-capstone-pythonic-refactor-studio-supplemental-2', {'affected_modules', 'dependency_map'}),
    ('PDP-24-pdp12-capstone-pythonic-refactor-studio-supplemental-3', {'make_registry', 'render_document'}),
    ('PDP-13-pdp7-state-and-command-supplemental-2', {'run_queue', 'make_increment'}),
    ('PDP-14-pdp7-state-and-command-supplemental-3', {'undo_edit', 'apply_edit'}),
    ('PDP-15-pdp8-adapter-and-integration-boundaries-supplemental-2', {'measurement_payload', 'parse_measurement'}),
    ('PDP-16-pdp8-adapter-and-integration-boundaries-supplemental-3', {'highest_value', 'fetch_values'}),
    ('PDP-09-pdp5-observer-events-and-callbacks-supplemental-2', {'subscribe', 'publish_snapshot'}),
    ('PDP-10-pdp5-observer-events-and-callbacks-supplemental-3', {'deliver', 'close'}),
    ('PDP-11-pdp6-decorator-proxy-and-facade-supplemental-2', {'compose_layers', 'make_traced'}),
    ('PDP-12-pdp6-decorator-proxy-and-facade-supplemental-3', {'run_resources', 'managed_resource'}),
    ('PDP-05-pdp3-strategy-without-ceremony-supplemental-2', {'make_bonus_rule', 'run_rule'}),
    ('PDP-06-pdp3-strategy-without-ceremony-supplemental-3', {'register_score_rule', 'choose_best'}),
    ('PDP-07-pdp4-factory-and-builder-in-python-supplemental-2', {'render_text', 'add_section'}),
    ('PDP-08-pdp4-factory-and-builder-in-python-supplemental-3', {'load_provider', 'select_provider'}),
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
