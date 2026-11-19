# Characterization Before Extraction

This complete reference implements the same public contract as the learner scaffold. Compare only after recording a passing learner baseline; additional structural choices remain open.

## Contract

Treat the supplied complete format_legacy function as the baseline. Extract rendering while preserving filtering before title/body access, output order and duplicates, title/body trimming/casing, raw kind matching and original KeyError priority. In particular, padded BLOG remains OTHER; an active filter on a record missing both kind/title raises KeyError(kind), while the all filter first raises KeyError(title). capture_outcome explicitly records either the returned string or exception class/message for comparison; this diagnostic deliberately captures Exception values. Keep input records unchanged.

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
baseline: ('returned', '[OTHER] hello: world')
same: True
```

## Evidence

Retain the five passing contract groups, the fresh strict-type result, exact driver output, one input/error trace and a small commit or exported rollback copy. Record the design pressure, the simpler alternative, the responsibility boundary and one remaining tradeoff. A deliberately changed rule belongs in a separately named check and change.
