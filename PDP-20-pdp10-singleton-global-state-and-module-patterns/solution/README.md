# Request Context and Module Cache

This complete reference implements the same public contract as the learner scaffold. Compare only after recording a passing learner baseline; additional structural choices remain open.

## Contract

Keep only an immutable request identifier in a module-level ContextVar. Set/reset its token in a context manager, preserving nested values, exception/cancellation cleanup, copied contexts and isolation between concurrent tasks. current_request raises LookupError when absent. remember uses a separate process-wide string cache: the first nonempty value for a key wins until clear_cache. Ordinary re-imports share that module/cache. cache_snapshot returns an independent dictionary, and tests/owners explicitly clear process data at teardown. This cache owns no file/network resource and the ContextVar carries no service objects.

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
inside: inner
restored: outer
copied: outer
cached: first first
cache after shutdown: {}
```

## Evidence

Retain the five passing contract groups, the fresh strict-type result, exact driver output, one input/error trace and a small commit or exported rollback copy. Record the design pressure, the simpler alternative, the responsibility boundary and one remaining tradeoff. A deliberately changed rule belongs in a separately named check and change.
