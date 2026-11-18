"""Independent acceptance for the foundations source pairs and static boundary."""
import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
FOLDERS = [
    "PDP-03-pdp2-design-foundations-in-python-supplemental-2",
    "PDP-04-pdp2-design-foundations-in-python-supplemental-3",
]


def load(index, role):
    name = f"foundation_{index}_{role}"
    spec = importlib.util.spec_from_file_location(
        name, ROOT / FOLDERS[index] / role / "main.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class FoundationContracts(unittest.TestCase):
    def test_reference_passes_each_supplied_learner_contract(self):
        for folder in FOLDERS:
            with self.subTest(folder=folder):
                result = subprocess.run(
                    [sys.executable, "-B", "-m", "unittest", "discover",
                     "-s", ".", "-p", "test_contract.py", "-v"],
                    cwd=ROOT / folder / "solution",
                    capture_output=True, text=True, timeout=20)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("Ran 5 tests", result.stderr)

    def test_starters_require_the_declared_work(self):
        first, second = load(0, "starter"), load(1, "starter")
        actions = [
            lambda: first.render_notice(first.Notice("build", "ready")),
            lambda: first.deliver_notice(first.Notice("build", "ready"),
                                        first.MemorySender()),
            lambda: second.new_task("plan"),
            lambda: second.snapshot_task(second.TaskRecord("plan")),
        ]
        for action in actions:
            with self.assertRaises(NotImplementedError):
                action()
        for folder in FOLDERS:
            result = subprocess.run(
                [sys.executable, "-B", "main.py"],
                cwd=ROOT / folder / "starter",
                capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(result.stdout.startswith("PDP2 starter unfinished:"))

    def test_complete_reference_outputs(self):
        expected = [
            "rendered: [build] ready\n"
            "first: ['[build] ready', '[build] ']\n"
            "second: ['[build] ready']\n",
            "first: {'name': 'plan', 'tags': ['new', 'ready']}\n"
            "second: {'name': 'other', 'tags': []}\n"
            "snapshot: {'name': 'plan', 'tags': ['new']}\n",
        ]
        for folder, output in zip(FOLDERS, expected):
            result = subprocess.run(
                [sys.executable, "-B", "main.py"],
                cwd=ROOT / folder / "solution",
                capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, output)
            self.assertEqual(result.stderr, "")

    def check_consumer(self, parameter_type):
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copyfile(ROOT / FOLDERS[0] / "solution/main.py",
                            Path(tmp, "main.py"))
            Path(tmp, "consumer.py").write_text(
                "from main import Notice, deliver_notice\n"
                "class SeparateSender:\n"
                f"    def send(self, body: {parameter_type}) -> None:\n"
                "        pass\n"
                "deliver_notice(Notice('build', 'ready'), SeparateSender())\n")
            return subprocess.run(
                [sys.executable, "-m", "mypy", "--strict",
                 "--python-version", "3.14", "--no-incremental",
                 "--cache-dir", str(Path(tmp, "mypy-cache")), "consumer.py"],
                cwd=tmp, capture_output=True, text=True, timeout=45)

    def test_static_protocol_accepts_an_unrelated_conforming_class(self):
        result = self.check_consumer("str")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Success: no issues found", result.stdout)

    def test_static_protocol_rejects_incompatible_parameter_type(self):
        result = self.check_consumer("int")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("[arg-type]", result.stdout)
        self.assertIn("SeparateSender", result.stdout)
        self.assertIn("Sender", result.stdout)


if __name__ == "__main__":
    unittest.main()
