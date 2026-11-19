# Pure Preparation and External Writes

Complete only the declared bodies: normalize_rows, publish_rows. The other definitions and the five contract groups provide the starting boundary. The untouched driver reports unfinished work; it becomes the passing baseline after those bodies are complete.

## Contract

normalize_rows owns a tuple of text rows, strips whitespace, drops blank rows and preserves duplicate/order. Reject nontext rows. publish_rows first validates its writer and completely prepares input before any write, then calls the writer in order and returns the number of successful writes only after full success. A source/preparation failure produces no writes. A writer failure propagates the same exception and stops later calls; earlier external writes remain. Callback mutation cannot extend the owned preparation snapshot.

## Run and verify

Use Python 3.14 in the exported folder. The program uses the standard library. The unchanged development requirements pin the static checker and its supporting packages.

```sh
python3.14 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -B main.py
.venv/bin/python -B -m unittest discover -s . -p test_contract.py -v
.venv/bin/python -m mypy --strict --no-incremental --python-version 3.14 main.py
```

On Windows use `py -3.14 -m venv .venv` and `.venv\Scripts\python.exe` for the later commands. Record the interpreter path/version and checker version. In the site IDE, confirm import, complete the bodies, save, run and export the complete project for these native checks.

After completion, the exact driver output is:

```text
written: ['alpha', 'beta']
count: 2
```

## Evidence

Retain the five passing contract groups, the fresh strict-type result, exact driver output, one input/error trace and a small commit or exported rollback copy. Record the design pressure, the simpler alternative, the responsibility boundary and one remaining tradeoff. A deliberately changed rule belongs in a separately named check and change.
