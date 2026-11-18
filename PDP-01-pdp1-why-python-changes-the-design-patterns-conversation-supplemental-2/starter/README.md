# Callable comparison

Compare a function, a configured closure and an immutable callable object. They share the callable contract `str -> str`; the driver uses behavior without requiring inheritance.

Complete only `title_case`, `make_prefix_formatter` and `PrefixFormatter.__call__`. Validation, object construction, the message driver and sample inputs are supplied.

- `title_case(text)` validates a string and applies Python's `str.title()`. Surrounding whitespace remains. This is Python's string operation, not a natural-language title editor.
- `make_prefix_formatter(prefix)` validates the prefix at construction and returns a closure. Each call validates text and returns prefix + text.
- `PrefixFormatter(prefix)` stores inspectable, immutable configuration and gives the same results as the closure.
- `format_messages(messages, formatter)` returns a new list in order, including from a one-pass iterable. Empty input returns an empty list. Invalid message or formatter output raises `TypeError`; formatter exceptions propagate.

For `["design patterns", ""]`, title formatting gives `["Design Patterns", ""]`. Either prefix formatter with `"LOG: "` gives `["LOG: design patterns", "LOG: "]`. Prefixes are exact: no spacing or punctuation is inserted. Differently configured formatters keep independent prefixes.

From this imported folder:

```sh
python3.14 -B main.py
python3.14 -B -m unittest discover -s . -p test_contract.py -v
```

The untouched starter reports unfinished work and its tests fail. Completing the three bodies makes all five contract tests pass. This lab uses only the standard library.

Explain which representation is sufficient without configuration, when one immutable value is captured, and when configuration needs an inspectable name. A callable object serves that requirement rather than a rule that every strategy needs a class.

Transfer practice: supply an independent uppercase callable and a generator of two messages; preserve ordering and the original list. Compare the reference after an attempt, beginning with contracts and tradeoffs.

Primary reference: [Python callable protocols](https://docs.python.org/3.14/library/typing.html#typing.Protocol).

## Native type check

Create a CPython 3.14 environment with `python3.14 -m venv .venv`. On macOS/Linux, install the pinned checker with `.venv/bin/python -m pip install -r requirements-dev.txt`, then run `.venv/bin/python -m mypy --strict --no-incremental --python-version 3.14 main.py`. On Windows, use `py -3.14` to create the environment and `.venv\Scripts\python.exe` for later commands.

Run the same contract tests with the environment's Python. After completing the required bodies, record a passing contract run and type check as the baseline before comparing structures. Python annotations describe the contract; supplied runtime validation enforces the declared string boundaries.
