# Managed Generator Lifetime

Complete only the declared bodies: managed_values, take_values. The other definitions and the five contract groups provide the starting boundary. The untouched driver reports unfinished work; it becomes the passing baseline after those bodies are complete.

## Contract

Validate and snapshot the integer input before acquisition. The surrounding managed_values context owns a real StringIO resource and closes both its generator and resource exactly once on exit, including zero consumption, partial consumption, early break and a consumer exception. Closing the inner generator stops iteration while the outer owner retains the resource until context exit. take_values consumes at most a nonnegative integer count, rejects bool, and leaves caller-owned iteration open. A body exception retains its identity after successful cleanup.

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
partial: [3, 5]
after: closed
events: ['open', 'close']
```

## Evidence

Retain the five passing contract groups, the fresh strict-type result, exact driver output, one input/error trace and a small commit or exported rollback copy. Record the design pressure, the simpler alternative, the responsibility boundary and one remaining tradeoff. A deliberately changed rule belongs in a separately named check and change.
