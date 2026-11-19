import unittest
from main import SourceError, fetch_values, highest_value

class Contracts(unittest.TestCase):
    def test_values_are_owned_and_reader_is_called_once(self):
        raw={"values":[2,4]}; calls=[]
        def read(): calls.append(1); return raw
        result=fetch_values(read); raw["values"].append(9)
        self.assertEqual(result,(2,4)); self.assertEqual(calls,[1])
    def test_empty_and_negative_maximum(self):
        self.assertEqual(fetch_values(lambda:{}),())
        with self.assertRaises(ValueError): highest_value(lambda:{})
        self.assertEqual(highest_value(lambda:{"values":[-5,-2,-9],"vendor":"ignored"}),-2)
    def test_vendor_failure_keeps_original_cause(self):
        for error in [TimeoutError("timeout"),OSError("offline")]:
            def read(): raise error
            with self.assertRaises(SourceError) as caught: fetch_values(read)
            self.assertIs(caught.exception.__cause__,error)
    def test_programming_error_is_not_reclassified(self):
        error=LookupError("bug")
        def read(): raise error
        with self.assertRaises(LookupError) as caught: highest_value(read)
        self.assertIs(caught.exception,error)
    def test_invalid_external_shapes_are_rejected(self):
        for raw in [None, [], {"values":None}, {"values":(1,)}, {"values":[True]}, {"values":[1.5]}, {"values":["2"]}]:
            with self.subTest(raw=raw), self.assertRaises(TypeError): fetch_values(lambda:raw)

if __name__ == "__main__": unittest.main()
