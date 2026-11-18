"""Native qualification for the event/wrapper source increment."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
FAMILIES = {'PDP3-Observer-Notification-Hub': 15, 'PDP4-Decorator-Proxy-Facade-Toolkit': 12, 'PDP-09-pdp5-observer-events-and-callbacks-supplemental-2': 5, 'PDP-10-pdp5-observer-events-and-callbacks-supplemental-3': 5, 'PDP-11-pdp6-decorator-proxy-and-facade-supplemental-2': 5, 'PDP-12-pdp6-decorator-proxy-and-facade-supplemental-3': 5}
OUTPUTS = ['summary: A-102 -> shipped\nemail: sent shipped message to ada@example.com\naudit: order=A-102 status=shipped\nemail: sent delivered message to ada@example.com\naudit: order=A-102 status=delivered\n', 'log: calling get_profile\nada -> plan=pro status=active billing=paid\nada -> plan=pro status=active billing=paid\n', "delivery: ['order:3', 'audit:3']\n", "inside: ['ready']\nafter: ['ready']\n", "result: 9\ntrace: ['audit:before', 'metrics:before', 'metrics:after', 'audit:after']\n", "result: complete\ntrace: ['acquire:profile', 'acquire:billing', 'body', 'release:billing', 'release:profile']\n"]
CLIENT_OUTPUTS = ["audit: ['A-102:shipped', 'B-205:packed', 'A-102:delivered']\ndashboard: ['A-102:shipped', 'B-205:packed']\n", 'initial: ada -> plan=pro status=active billing=paid\ncached: ada -> plan=pro status=active billing=paid\nloads: 1\nrevoked: PermissionError\nfresh: ada -> plan=team status=active billing=paid\nloads: 2\n']

class EventsWrappersAcceptance(unittest.TestCase):
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
