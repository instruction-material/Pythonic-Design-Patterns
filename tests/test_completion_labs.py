"""Native contracts for pipeline/global-state/refactoring completion sources."""
from pathlib import Path
import hashlib
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
FAMILIES={'PDP-17-pdp9-template-method-versus-higher-order-functions-supplemental-2': 5, 'PDP-18-pdp9-template-method-versus-higher-order-functions-supplemental-3': 5, 'PDP-19-pdp10-singleton-global-state-and-module-patterns': 5, 'PDP-20-pdp10-singleton-global-state-and-module-patterns': 5, 'PDP-21-pdp11-refactoring-python-code-smells-supplemental-2': 5, 'PDP-22-pdp11-refactoring-python-code-smells-supplemental-3': 5, 'PDP-23-pdp12-capstone-pythonic-refactor-studio-supplemental-2': 5, 'PDP-24-pdp12-capstone-pythonic-refactor-studio-supplemental-3': 5, 'PDP7-Pythonic-Refactor-Capstone': 15}
OUTPUTS={'PDP-17-pdp9-template-method-versus-higher-order-functions-supplemental-2': 'functional: [4, 6]\ntemplate: [4, 6]\ninput: [1, 2]\n', 'PDP-18-pdp9-template-method-versus-higher-order-functions-supplemental-3': "partial: [3, 5]\nafter: closed\nevents: ['open', 'close']\n", 'PDP-19-pdp10-singleton-global-state-and-module-patterns': "first: A:hello\nsecond: B:world\nindependent: ('A:hello',) ('B:world',)\nclosed: True True\n", 'PDP-20-pdp10-singleton-global-state-and-module-patterns': 'inside: inner\nrestored: outer\ncopied: outer\ncached: first first\ncache after shutdown: {}\n', 'PDP-21-pdp11-refactoring-python-code-smells-supplemental-2': "baseline: ('returned', '[OTHER] hello: world')\nsame: True\n", 'PDP-22-pdp11-refactoring-python-code-smells-supplemental-3': "written: ['alpha', 'beta']\ncount: 2\n", 'PDP-23-pdp12-capstone-pythonic-refactor-studio-supplemental-2': "imports: {'app': ('model', 'render'), 'model': (), 'render': ('model',)}\naffected by model: ('app', 'model', 'render')\n", 'PDP-24-pdp12-capstone-pythonic-refactor-studio-supplemental-3': 'baseline: [BLOG] hello: world\nreplaced: hello | world\n', 'PDP7-Pythonic-Refactor-Capstone': '[BLOG] hello world: python patterns\n[NEWS] system update: adapters and facades\n'}
CLIENT_OUTPUTS={'pdp9_comparison.py': 'csv forms equal: True\nwebhook forms equal: True\nreplacement scores: [7, 9]\nreplacement equal: True\n', 'pdp9_failure_client.py': "class same failure: True\nclass events: ['adapt:first', 'transform:first', 'adapt:second', 'transform:second']\ncallable same failure: True\ncallable events: ['adapt:first', 'transform:first', 'adapt:second', 'transform:second']\n", 'comparison_client.py': 'replacement: hello world\nsaved: [\'hello world\']\njson: [{"title":"hello world","kind":"blog","body":"python patterns"}]\n'}


class CompletionSources(unittest.TestCase):
    def run_file(self, folder, role, name):
        result=subprocess.run([sys.executable,"-B",name],cwd=ROOT/folder/role,
                              capture_output=True,text=True,timeout=15)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertEqual(result.stderr,"")
        return result.stdout

    def test_nine_references_pass_public_contracts(self):
        for folder,count in FAMILIES.items():
            with self.subTest(folder=folder):
                result=subprocess.run([sys.executable,"-B","-m","unittest","discover",
                    "-s",".","-p","test_contract.py","-v"],cwd=ROOT/folder/"solution",
                    capture_output=True,text=True,timeout=30)
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
                self.assertIn(f"Ran {count} tests",result.stderr)

    def test_complete_capstone_baseline_passes_same_contracts(self):
        result=subprocess.run([sys.executable,"-B","-m","unittest","discover",
            "-s",".","-p","test_contract.py","-v"],
            cwd=ROOT/"PDP7-Pythonic-Refactor-Capstone/starter",
            capture_output=True,text=True,timeout=30)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertIn("Ran 15 tests",result.stderr)

    def test_exact_outputs_and_unfinished_scaffolds(self):
        for folder,output in OUTPUTS.items():
            with self.subTest(folder=folder):
                self.assertEqual(self.run_file(folder,"solution","main.py"),output)
                initial=self.run_file(folder,"starter","main.py")
                if folder=="PDP7-Pythonic-Refactor-Capstone": self.assertEqual(initial,output)
                else: self.assertIn("starter unfinished: Complete ",initial)

    def test_standalone_extension_clients_in_both_roles(self):
        for filename,output in CLIENT_OUTPUTS.items():
            folder=("PDP7-Pythonic-Refactor-Capstone" if filename=="comparison_client.py"
                    else "PDP6-Adapter-Template-Import-Pipeline")
            for role in ("starter","solution"):
                with self.subTest(file=filename,role=role):
                    self.assertEqual(self.run_file(folder,role,filename),output)

    def test_each_role_has_exact_pins_brief_and_same_oracle(self):
        pins=(ROOT/"requirements-dev.txt").read_bytes()
        for folder in FAMILIES:
            for role in ("starter","solution"):
                target=ROOT/folder/role
                self.assertEqual((target/"requirements-dev.txt").read_bytes(),pins)
                self.assertIn("Python 3.14",(target/"README.md").read_text())
        oracle=(ROOT/"PDP7-Pythonic-Refactor-Capstone/starter/baseline_original.py").read_text()
        self.assertEqual(oracle,(ROOT/"PDP7-Pythonic-Refactor-Capstone/solution/baseline_original.py").read_text())
        self.assertEqual(hashlib.sha256(oracle.encode()).hexdigest(),'bac4d05d399d0b801aef75ecf93bae46e67c1f3d992366a2458b8220c879435b')


if __name__=="__main__": unittest.main()
