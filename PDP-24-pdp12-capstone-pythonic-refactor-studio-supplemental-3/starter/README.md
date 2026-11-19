# Replace a Renderer Through a Boundary

Complete only the declared bodies: make_registry, render_document. The other definitions and the five contract groups provide the starting boundary. The untouched driver reports unfinished work; it becomes the passing baseline after those bodies are complete.

## Contract

Copy and freeze a registry with nonempty trimmed text names and callable renderers. Snapshot immutable Article values and validate setup/data before invoking renderers. Select by exact kind with an explicit fallback; retain order/duplicates, require text results and join with newline. An empty input returns empty text. A callback failure retains identity and stops later calls; external effects are not undone. Replacing a blog renderer changes its rows while the fallback rows retain their exact behavior.

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
baseline: [BLOG] hello: world
replaced: hello | world
```

## Evidence

Retain the five passing contract groups, the fresh strict-type result, exact driver output, one input/error trace and a small commit or exported rollback copy. Record the design pressure, the simpler alternative, the responsibility boundary and one remaining tradeoff. A deliberately changed rule belongs in a separately named check and change.
