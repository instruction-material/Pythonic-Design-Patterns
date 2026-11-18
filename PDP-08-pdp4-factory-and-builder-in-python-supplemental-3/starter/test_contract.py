import unittest
import sys
from main import ProviderSpec, ProviderLoadError, load_provider, select_provider, metadata_fixture


class ProviderContract(unittest.TestCase):
    def test_single_pass_and_selected_loader_only(self):
        seen = []
        def selected():
            seen.append("selected")
            return lambda text: "[" + text + "]"
        def unused():
            seen.append("unused")
            raise AssertionError("must stay unloaded")
        candidates = (p for p in [ProviderSpec("skip", unused), ProviderSpec("ok", selected)])
        provider = load_provider("ok", candidates)
        self.assertEqual(provider("ready"), "[ready]")
        self.assertEqual(seen, ["selected"])
        with metadata_fixture() as (actual, module_name):
            self.assertEqual([candidate.name for candidate in actual], ["bracket"])
            self.assertNotIn(module_name, sys.modules)
            function = load_provider("bracket", actual)
            self.assertEqual(function("ready"), "[ready]")
            self.assertIn(module_name, sys.modules)
        self.assertNotIn(module_name, sys.modules)

    def test_missing_and_duplicate_before_load(self):
        seen = []
        def loader():
            seen.append("loaded")
            return str
        first = ProviderSpec("same", loader)
        with self.assertRaises(LookupError): load_provider("missing", [first])
        with self.assertRaises(ValueError): load_provider("same", [first, first])
        self.assertEqual(seen, [])
        for entries in [(), (("same", "bracket"), ("same", "bracket"))]:
            with metadata_fixture(entries) as (actual, module_name):
                self.assertNotIn(module_name, sys.modules)
                expected = LookupError if not entries else ValueError
                with self.assertRaises(expected):
                    load_provider("same", actual)
                self.assertNotIn(module_name, sys.modules)
        with metadata_fixture((("first", "bracket"), ("second", "bracket"))) as (actual, module_name):
            self.assertEqual(len(actual), 2)
            self.assertNotIn(module_name, sys.modules)
            self.assertEqual(load_provider("second", actual)("two"), "[two]")

    def test_failure_cause_and_no_retry(self):
        seen = []
        error = OSError("broken import")
        def loader():
            seen.append("loaded")
            raise error
        with self.assertRaises(ProviderLoadError) as result:
            load_provider("bad", [ProviderSpec("bad", loader)])
        self.assertIs(result.exception.__cause__, error)
        self.assertEqual(seen, ["loaded"])
        with metadata_fixture((("broken", "missing_attribute"),)) as (actual, module_name):
            self.assertNotIn(module_name, sys.modules)
            with self.assertRaises(ProviderLoadError) as result:
                load_provider("broken", actual)
            self.assertIsInstance(result.exception.__cause__, AttributeError)

    def test_loaded_capability_boundary(self):
        with self.assertRaises(TypeError): load_provider("bad", [ProviderSpec("bad", lambda: 3)])
        def wrong_signature():
            return "no argument"
        provider = load_provider("callable", [ProviderSpec("callable", lambda: wrong_signature)])
        with self.assertRaises(TypeError): provider("actual call")

    def test_candidate_and_selection_validation(self):
        with self.assertRaises(ValueError): ProviderSpec(" ", lambda: str)
        with self.assertRaises(TypeError): ProviderSpec("ok", None)
        with self.assertRaises(TypeError): select_provider(None, [])
        with self.assertRaises(ValueError): select_provider(" ", [])
        with self.assertRaises(TypeError): select_provider("ok", [object()])


if __name__ == "__main__": unittest.main()
