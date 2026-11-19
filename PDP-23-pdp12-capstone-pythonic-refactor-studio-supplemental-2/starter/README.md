# Dependency Map and Change Surface

Complete only the declared bodies: dependency_map, affected_modules. The other definitions and the five contract groups provide the starting boundary. The untouched driver reports unfinished work; it becomes the passing baseline after those bodies are complete.

## Contract

Parse text for flat, valid Python module identifiers without executing it. Include statically declared internal imports, including aliases and imports inside branches/functions; ignore external imports. Sort/deduplicate edges and own the result. This lexical map does not measure dynamic imports or executed branches; reject relative imports and package-layout identifiers explicitly. Preserve SyntaxError with its source filename. affected_modules includes the changed module and all transitive dependents, handles cycles, validates all graph edges and returns a sorted tuple; an unknown changed module raises KeyError.

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
imports: {'app': ('model', 'render'), 'model': (), 'render': ('model',)}
affected by model: ('app', 'model', 'render')
```

## Evidence

Retain the five passing contract groups, the fresh strict-type result, exact driver output, one input/error trace and a small commit or exported rollback copy. Record the design pressure, the simpler alternative, the responsibility boundary and one remaining tradeoff. A deliberately changed rule belongs in a separately named check and change.
