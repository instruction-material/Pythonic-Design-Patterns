import inspect
import unittest
from main import calculate, compose_layers, make_traced

class TransparentTraceContracts(unittest.TestCase):
    def test_positional_keywords_return_and_complete_stack_order(self):
        trace = []
        wrapped = compose_layers(calculate, ["audit", "metrics"], trace)
        self.assertEqual(wrapped(4, offset=1), 9)
        self.assertEqual(trace, ["audit:before", "metrics:before", "metrics:after", "audit:after"])

    def test_metadata_signature_and_unwrapped_core_are_preserved(self):
        trace = []
        wrapped = make_traced("audit", trace, calculate)
        for name in ["__name__", "__doc__", "__annotations__"]:
            self.assertEqual(getattr(wrapped, name), getattr(calculate, name))
        self.assertEqual(inspect.signature(wrapped), inspect.signature(calculate))
        self.assertIs(wrapped.__wrapped__, calculate)
        self.assertEqual(wrapped.__wrapped__(4, offset=3), 11)
        self.assertEqual(trace, [])

    def test_failure_propagates_after_reverse_order_cleanup_trace(self):
        trace, failure = [], OSError("core failure")
        def fail(value): raise failure
        wrapped = compose_layers(fail, ["a", "b"], trace)
        with self.assertRaises(OSError) as caught: wrapped(4)
        self.assertIs(caught.exception, failure)
        self.assertEqual(trace, ["a:before", "b:before", "b:after", "a:after"])

    def test_empty_and_duplicate_layers_keep_the_declared_order(self):
        trace = []
        self.assertIs(compose_layers(calculate, [], trace), calculate)
        wrapped = compose_layers(calculate, iter(["same", "same"]), trace)
        self.assertEqual(wrapped(0), 1)
        self.assertEqual(trace, ["same:before", "same:before", "same:after", "same:after"])

    def test_bad_labels_and_deferred_shapes_are_explicit(self):
        trace = []
        with self.assertRaises(ValueError): compose_layers(calculate, ["ok", " "], trace)
        with self.assertRaises(TypeError): make_traced(1, trace, calculate)
        with self.assertRaises(TypeError): make_traced("ok", trace, None)
        async def deferred(): return 1
        with self.assertRaises(TypeError): make_traced("ok", trace, deferred)
        self.assertEqual(trace, [])

if __name__ == "__main__": unittest.main()
