"""Native qualification for the state/adapter source increment."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
FAMILIES = {'PDP5-State-Command-Quest-Loop': 12, 'PDP6-Adapter-Template-Import-Pipeline': 10, 'PDP-13-pdp7-state-and-command-supplemental-2': 5, 'PDP-14-pdp7-state-and-command-supplemental-3': 5, 'PDP-15-pdp8-adapter-and-integration-boundaries-supplemental-2': 5, 'PDP-16-pdp8-adapter-and-integration-boundaries-supplemental-3': 5}
OUTPUTS = ['boss gate boss 2\nretained: 3\nreplay equal: True\n', "csv: [Lead(email='ada@example.com', source='csv', score=7), Lead(email='turing@example.com', source='csv', score=10)]\nwebhook: [Lead(email='hopper@example.com', source='webhook', score=10)]\nfunctional equal: True\n", 'result: 9\nconfig now: 100\n', 'edited: third\nundo: second\nundo: first\nempty: False\n', 'normalized: 2026-01-01T00:00:00+00:00 20.0 C\nround trip: True\n', 'highest: 9\nsource failure: TimeoutError\n']
CLIENT_OUTPUTS = ['retained: 2\nreplayed: camp 6\nundo floor: 4\nempty: False\n', 'default csv: 0\nwebhook priority: 10\ncustom score: 9\nfunctional/class equal: True\n']

class StateAdapterAcceptance(unittest.TestCase):
    def contracts(self, folder, role):
        result = subprocess.run(
            [sys.executable, "-B", "-m", "unittest", "discover", "-s", ".",
             "-p", "test_contract.py", "-v"], cwd=ROOT/folder/role,
            capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
        self.assertIn(f"Ran {FAMILIES[folder]} tests", result.stderr)

    def test_six_reference_families_pass_their_public_contracts(self):
        for folder in FAMILIES:
            with self.subTest(folder=folder): self.contracts(folder, "solution")

    def test_two_complete_baseline_starters_pass_the_same_contracts(self):
        for folder in list(FAMILIES)[:2]:
            with self.subTest(folder=folder): self.contracts(folder, "starter")

    def test_all_reference_driver_outputs_are_exact(self):
        for folder, output in zip(FAMILIES, OUTPUTS):
            result = subprocess.run([sys.executable,"-B","main.py"],
                cwd=ROOT/folder/"solution",capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(result.stdout,output)
            self.assertEqual(result.stderr,"")

    def test_complete_baseline_drivers_equal_reference_behavior(self):
        for folder, output in zip(list(FAMILIES)[:2], OUTPUTS):
            result = subprocess.run([sys.executable,"-B","main.py"],
                cwd=ROOT/folder/"starter",capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(result.stdout,output)

    def test_four_small_drivers_announce_the_declared_unfinished_work(self):
        for folder in list(FAMILIES)[2:]:
            result = subprocess.run([sys.executable,"-B","main.py"],
                cwd=ROOT/folder/"starter",capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertIn("starter unfinished: Complete ",result.stdout)

    def test_optional_reference_clients_are_complete_and_distinct(self):
        fence = chr(96)*3
        for folder, output in zip(list(FAMILIES)[:2], CLIENT_OUTPUTS):
            brief=(ROOT/folder/"solution/README.md").read_text()
            code=brief.split(fence+"python\n",1)[1].split(fence,1)[0]
            with tempfile.TemporaryDirectory() as tmp:
                shutil.copyfile(ROOT/folder/"solution/main.py",Path(tmp,"main.py"))
                Path(tmp,"client.py").write_text(code)
                result=subprocess.run([sys.executable,"-B","client.py"],cwd=tmp,
                    capture_output=True,text=True,timeout=10)
                self.assertEqual(result.returncode,0,result.stderr)
                self.assertEqual(result.stdout,output)

    def test_each_imported_role_has_its_brief_contract_and_exact_development_pins(self):
        pins=(ROOT/"requirements-dev.txt").read_bytes()
        for folder in FAMILIES:
            for role in ["starter","solution"]:
                target=ROOT/folder/role
                self.assertEqual((target/"requirements-dev.txt").read_bytes(),pins)
                self.assertIn("Python 3.14",(target/"README.md").read_text())
                self.assertTrue((target/"test_contract.py").is_file())

if __name__ == "__main__": unittest.main()
