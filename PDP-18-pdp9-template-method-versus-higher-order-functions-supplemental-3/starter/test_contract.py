import unittest
from io import StringIO
from unittest.mock import patch
import main as lab


class LifetimeContracts(unittest.TestCase):
    def test_partial_consumption_and_early_break_release(self):
        events = []
        with lab.managed_values([3, 5, 8], events) as values:
            self.assertEqual(events, ["open"])
            self.assertEqual(lab.take_values(values, 2), [3, 5])
        self.assertEqual(events, ["open", "close"])
        self.assertEqual(next(values, "closed"), "closed")
        events.clear()
        with lab.managed_values([1, 2], events) as values:
            for value in values:
                self.assertEqual(value, 1)
                break
        self.assertEqual(events, ["open", "close"])

    def test_never_consumed_empty_and_exhausted_streams(self):
        for data in [[], [1]]:
            events = []
            resources = []
            def opened(text):
                resource = StringIO(text)
                resources.append(resource)
                return resource
            with patch.object(lab, "StringIO", opened):
                with lab.managed_values(data, events):
                    self.assertFalse(resources[0].closed)
            self.assertTrue(resources[0].closed)
            self.assertEqual(events, ["open", "close"])
        events = []
        with lab.managed_values([1], events) as values:
            self.assertEqual(lab.take_values(values, 10), [1])
            self.assertEqual(lab.take_values(values, 1), [])
        self.assertEqual(events, ["open", "close"])

    def test_manual_close_does_not_transfer_outer_ownership(self):
        events = []
        with lab.managed_values([1, 2], events) as values:
            self.assertEqual(next(values), 1)
            values.close()
            self.assertEqual(next(values, "closed"), "closed")
            self.assertEqual(events, ["open"])
        self.assertEqual(events, ["open", "close"])

    def test_body_failure_keeps_exception_identity_and_releases(self):
        error = RuntimeError("consumer failed")
        events = []
        with self.assertRaises(RuntimeError) as caught:
            with lab.managed_values([1, 2], events) as values:
                self.assertEqual(next(values), 1)
                raise error
        self.assertIs(caught.exception, error)
        self.assertEqual(events, ["open", "close"])

    def test_owned_values_and_pre_acquisition_validation(self):
        data, events = [1, 2], []
        with lab.managed_values(data, events) as values:
            data.append(9)
            self.assertEqual(lab.take_values(values, 0), [])
            self.assertEqual(next(values), 1)
            for bad in [-1, True, "2"]:
                with self.assertRaises((TypeError, ValueError)):
                    lab.take_values(values, bad)
            self.assertEqual(next(values), 2)
        for bad in [True, "2"]:
            events = []
            with self.assertRaises(TypeError):
                with lab.managed_values([1, bad], events):
                    pass
            self.assertEqual(events, [])


if __name__ == "__main__":
    unittest.main()
