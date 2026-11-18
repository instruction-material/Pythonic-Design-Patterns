# Named callable registry

Select a callable by a caller-supplied name. The registry is explicit input rather than process-wide mutable state. A new operation is another callable entry; it requires no formatter subclass.

Complete only `make_rulebook` and `select_formatter`. The message driver, validation helper and sample input are supplied.

- `make_rulebook(prefix)` validates a string prefix and returns a fresh dictionary in this order: `title`, `prefix`, `identity`.
- `title` uses `str.title()`; `prefix` returns exact prefix + text; `identity` returns validated text unchanged.
- `select_formatter(name, rules)` validates the name and returns its callable without mutating rules. Missing names raise `ValueError` with the original `KeyError` as cause. Mapped non-callables raise `TypeError`.
- `format_named(messages, name, rules)` resolves the name once before iteration. It returns a fresh list in order, validates input/output strings and propagates callable failures. An unknown name fails even for empty messages.

For `["design patterns", ""]` with prefix `"LOG: "`, outputs are `["Design Patterns", ""]`, `["LOG: design patterns", "LOG: "]` and `["design patterns", ""]`. Empty prefixes are valid. A custom `reverse` callable maps `"abc"` to `"cba"` without inheritance.

From this imported folder:

```sh
python3.14 -B main.py
python3.14 -B -m unittest discover -s . -p test_contract.py -v
```

The untouched starter reports unfinished work and its tests fail. Completing the two bodies makes all five contract tests pass. No third-party packages are needed.

Extension practice: add `reverse` to one registry, create a second registry and prove the second is unchanged. Record the selection requirement, direct-function alternative, added lookup cost and a removal trigger. If callers no longer choose by name, passing one callable directly may suffice.

The design-journal activity is a written decision record. Its course case/template is separate from this executable extension activity.

Primary reference: [Python mapping interfaces](https://docs.python.org/3.14/library/collections.abc.html).

## Native type check

Create a CPython 3.14 environment with `python3.14 -m venv .venv`. On macOS/Linux, install the pinned checker with `.venv/bin/python -m pip install -r requirements-dev.txt`, then run `.venv/bin/python -m mypy --strict --no-incremental --python-version 3.14 main.py`. On Windows, use `py -3.14` to create the environment and `.venv\Scripts\python.exe` for later commands.

Run the same contract tests with the environment's Python. After completing the required bodies, record a passing contract run and type check as the baseline before comparing structures. Python annotations describe the contract; supplied runtime validation enforces the declared string boundaries.
