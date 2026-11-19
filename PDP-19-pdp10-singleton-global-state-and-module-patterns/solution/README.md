# Application Factory and Owned Services

This complete reference implements the same public contract as the learner scaffold. Compare only after recording a passing learner baseline; additional structural choices remain open.

## Contract

Create an Application from a frozen Config and an explicit store factory. Validate setup before invoking the factory, invoke it once, and require save/close methods. Each default factory call owns a fresh MemoryStore. run trims message text, prepends the configured prefix, saves once and returns that exact text. Close the owned service at most once, mark the application closed even if cleanup fails, and reject later runs/re-entry. Context exit closes the service; a body error propagates when cleanup succeeds. If cleanup also fails, ordinary Python exception chaining exposes both errors. Factory/store errors retain identity; no external save is rolled back.

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
first: A:hello
second: B:world
independent: ('A:hello',) ('B:world',)
closed: True True
```

## Evidence

Retain the five passing contract groups, the fresh strict-type result, exact driver output, one input/error trace and a small commit or exported rollback copy. Record the design pressure, the simpler alternative, the responsibility boundary and one remaining tradeoff. A deliberately changed rule belongs in a separately named check and change.
