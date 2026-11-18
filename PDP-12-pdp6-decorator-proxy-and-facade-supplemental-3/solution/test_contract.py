import unittest
from main import managed_resource, run_resources

class LifecycleContracts(unittest.TestCase):
    def test_empty_and_normal_reverse_cleanup(self):
        trace = []
        self.assertEqual(run_resources([], trace), "complete")
        self.assertEqual(trace, ["body"])
        trace.clear()
        self.assertEqual(run_resources(["profile", "billing"], trace), "complete")
        self.assertEqual(trace, ["acquire:profile", "acquire:billing", "body",
                                 "release:billing", "release:profile"])

    def test_partial_acquisition_failure_releases_only_acquired_resources(self):
        trace = []
        with self.assertRaises(OSError):
            run_resources(["a", "b", "c"], trace, fail_at="b")
        self.assertEqual(trace, ["acquire:a", "acquire:b", "failed:b", "release:a"])

    def test_body_exception_propagates_after_reverse_cleanup(self):
        trace = []
        with self.assertRaisesRegex(ValueError, "body failed"):
            run_resources(["a", "b"], trace, fail_body=True)
        self.assertEqual(trace, ["acquire:a", "acquire:b", "body", "release:b", "release:a"])

    def test_only_selected_value_error_suppression_changes_outcome(self):
        trace = []
        self.assertEqual(run_resources(["a", "b"], trace, fail_body=True, suppress_at="b"),
                         "suppressed")
        self.assertEqual(trace, ["acquire:a", "acquire:b", "body",
                                 "suppressed:b", "release:b", "release:a"])
        trace.clear()
        with self.assertRaises(OSError):
            run_resources(["a", "b"], trace, fail_at="b", suppress_at="a")
        self.assertEqual(trace, ["acquire:a", "acquire:b", "failed:b", "release:a"])

    def test_fresh_repeated_and_nested_contexts_and_validation(self):
        trace = []
        for _ in range(2):
            with managed_resource("a", trace) as name: self.assertEqual(name, "a")
        with managed_resource("outer", trace):
            with managed_resource("inner", trace): trace.append("nested")
        self.assertEqual(trace, ["acquire:a", "release:a", "acquire:a", "release:a",
                                 "acquire:outer", "acquire:inner", "nested",
                                 "release:inner", "release:outer"])
        trace.clear()
        with self.assertRaises(ValueError): run_resources(["a", " "], trace)
        with self.assertRaises(TypeError): run_resources([None], trace)
        self.assertEqual(trace, [])

if __name__ == "__main__": unittest.main()
