# Versioned Measurement Adapter

Translate v1 {version:1, timestamp:offset ISO text, temperature:{value:number,unit:C/F/K}} and v2 {version:2, measured_at:offset ISO text, kelvin:number} into an immutable UTC Measurement with Celsius units. Both versions require every shown field; version defaults to 1, extra fields are ignored, naive timestamps and nonfinite/bool temperatures are rejected. Export canonical v2 and verify round trips within floating-point tolerance. Preserve original validation errors as AdapterError causes.

Start in `starter/`; compare the complete reference in `solution/` after producing an independent attempt. Each imported role contains the runnable driver, contract tests and its brief.
