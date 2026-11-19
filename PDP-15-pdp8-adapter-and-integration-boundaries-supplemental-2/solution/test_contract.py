from dataclasses import FrozenInstanceError
from datetime import UTC, datetime
import unittest
from main import AdapterError, Measurement, measurement_payload, parse_measurement

class Contracts(unittest.TestCase):
    def test_fahrenheit_and_offset_normalize(self):
        raw = {"timestamp":"2026-01-01T02:00:00+02:00", "temperature":{"value":68,"unit":"F"}, "extra":123}
        value = parse_measurement(raw)
        self.assertEqual(value.instant, datetime(2026,1,1,tzinfo=UTC)); self.assertAlmostEqual(value.celsius,20)
        self.assertEqual(raw["temperature"]["value"],68)
    def test_versions_and_all_units(self):
        for unit, amount in [("C",20),("F",68),("K",293.15)]:
            value = parse_measurement({"version":1,"timestamp":"2026-01-01T00:00:00Z","temperature":{"value":amount,"unit":unit}})
            self.assertAlmostEqual(value.celsius,20)
        self.assertAlmostEqual(parse_measurement({"version":2,"measured_at":"2026-01-01T00:00:00Z","kelvin":293.15}).celsius,20)
    def test_round_trip_retains_instant_and_quantity(self):
        for temperature in [-273.15, -12.75, 0, 23.4, 1000]:
            value = Measurement(datetime(2026,1,1,tzinfo=UTC), temperature)
            result = parse_measurement(measurement_payload(value))
            self.assertEqual(result.instant,value.instant); self.assertAlmostEqual(result.celsius,value.celsius)
    def test_malformed_inputs_have_original_causes(self):
        base={"timestamp":"2026-01-01T00:00:00Z","temperature":{"value":1,"unit":"C"}}
        cases=[{}, dict(base,version=3), dict(base,version=True), dict(base,timestamp="2026-01-01"), dict(base,temperature={"value":True,"unit":"C"}), dict(base,temperature={"value":float("nan"),"unit":"C"}), dict(base,temperature={"value":-1,"unit":"K"}), dict(base,temperature={"value":1,"unit":"X"})]
        for raw in cases:
            with self.subTest(raw=raw), self.assertRaises(AdapterError) as caught: parse_measurement(raw)
            self.assertIsNotNone(caught.exception.__cause__)
    def test_internal_measurement_is_immutable_and_aware(self):
        value=Measurement(datetime(2026,1,1,tzinfo=UTC), 1)
        with self.assertRaises(FrozenInstanceError): value.celsius=2
        with self.assertRaises(ValueError): Measurement(datetime(2026,1,1),1)
        with self.assertRaises(TypeError): measurement_payload({})

if __name__ == "__main__": unittest.main()
