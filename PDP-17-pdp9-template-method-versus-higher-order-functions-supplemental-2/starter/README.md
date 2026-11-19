# Named Stages and Template Hooks

Complete only the declared bodies: compose_stages, run_steps. The other definitions and the five contract groups provide the starting boundary. The untouched driver reports unfinished work; it becomes the passing baseline after those bodies are complete.

## Contract

Snapshot and validate integer input before callbacks. Compose stages in the supplied order; an empty composition is the identity. Validate integer results and reject bool. Stop at the first callback exception and preserve that exact exception object; prior external callback effects remain. The TemplatePipeline skeleton and AddThenDouble hook must agree with the equivalent callable composition.

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
functional: [4, 6]
template: [4, 6]
input: [1, 2]
```

## Evidence

Retain the five passing contract groups, the fresh strict-type result, exact driver output, one input/error trace and a small commit or exported rollback copy. Record the design pressure, the simpler alternative, the responsibility boundary and one remaining tradeoff. A deliberately changed rule belongs in a separately named check and change.
