# Versioned Measurement Adapter

Python 3.14. Translate v1 {version:1, timestamp:offset ISO text, temperature:{value:number,unit:C/F/K}} and v2 {version:2, measured_at:offset ISO text, kelvin:number} into an immutable UTC Measurement with Celsius units. Both versions require every shown field; version defaults to 1, extra fields are ignored, naive timestamps and nonfinite/bool temperatures are rejected. Export canonical v2 and verify round trips within floating-point tolerance. Preserve original validation errors as AdapterError causes.

Run `python3.14 -B main.py` and `python3.14 -B -m unittest discover -s . -p test_contract.py -v`. After completion, the driver output is:

```text
normalized: 2026-01-01T00:00:00+00:00 20.0 C
round trip: True
```

The contract suite has five behavioral groups. Development pins are installed with `python3.14 -m pip install -r requirements-dev.txt`; runtime code uses the standard library.
