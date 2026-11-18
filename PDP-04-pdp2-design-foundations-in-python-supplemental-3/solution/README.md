# Owned mutable records and snapshots

Reference implementation. The learner completes only `new_task` and `snapshot_task`. TaskRecord, TaskSnapshot, validation helpers and the demonstration are supplied.

## Observable contract

- A record's name and every tag are strings containing a non-space character. Preserve their exact values, order and duplicates. Non-string values raise TypeError; blank strings raise ValueError.
- `new_task(name,tags=())` consumes the tag iterable once and creates a new owned list. Lists, tuples and generators are supported. A string or bytes value used as the entire tag iterable raises TypeError.
- Default tag lists belong to individual TaskRecord instances. Changing one record leaves another record and the original caller-owned list unchanged.
- `snapshot_task(record)` validates the current record and returns a new dictionary with name and a copied tags list. Later changes to either list stay separate.
- A non-TaskRecord, a current tags value that is not a list, or invalid current field values are rejected at the snapshot boundary. TaskRecord is deliberately mutable; type annotations alone do not prevent a caller from changing its fields incorrectly.

For `new_task("plan",["new"])`, the snapshot is `{"name":"plan","tags":["new"]}`. Appending `"ready"` to the record leaves the earlier snapshot at `["new"]`. Appending to the snapshot leaves the record unchanged. `["b","a","b"]` stays in that order with both copies of b.

## Work and evidence

Complete the two bodies, run the five contracts, and explain the two different ownership boundaries: caller to record, then record to snapshot. Include one one-pass generator case and one invalid state introduced after construction.

The completed demonstration prints:

```text
first: {'name': 'plan', 'tags': ['new', 'ready']}
second: {'name': 'other', 'tags': []}
snapshot: {'name': 'plan', 'tags': ['new']}
```

TaskRecord compares by its field values and is unhashable because it is a mutable data class. Store a stable identifier as a dictionary key. A frozen data class also needs suitable field values before it can be safely used as a key.

## Native verification

Use CPython 3.14 and create a virtual environment in the exported folder. On macOS/Linux:

```sh
python3.14 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -B main.py
.venv/bin/python -B -m unittest discover -s . -p test_contract.py -v
.venv/bin/python -m mypy --strict --no-incremental --python-version 3.14 main.py
```

On Windows, create the environment with `py -3.14 -m venv .venv` and use `.venv\Scripts\python.exe` for the later commands. The untouched scaffold reports `PDP2 starter unfinished`; its contracts pass after the declared bodies are completed.

In the site IDE, confirm the import, edit and save, then export all four files for native verification. Keep the bundled browser interpreter's version separate from the native baseline.

[Data-class documentation](https://docs.python.org/3.14/library/dataclasses.html)
