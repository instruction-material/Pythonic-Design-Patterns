# Composed notice delivery

Reference implementation. The learner completes only `render_notice` and `deliver_notice` in the learner scaffold. The validated Notice value, Sender protocol, MemorySender, validation helpers and demonstration are supplied.

## Observable contract

- A Notice contains topic and text strings. Its topic must contain a non-space character; empty text is valid. Non-string fields raise TypeError and blank topics raise ValueError. Fields retain their original whitespace.
- `render_notice(notice)` returns `[topic] text` without delivery or mutation. A non-Notice argument raises TypeError.
- `deliver_notice(notice,sender)` renders once, calls `sender.send(rendered)` exactly once, and returns that same string. A sender supplies a synchronous method accepting one positional string. It can be a separate class satisfying the protocol.
- A missing or non-callable send attribute raises TypeError. A sender exception propagates unchanged; the driver performs no retry.
- Every MemorySender owns its message list. Notice is frozen against ordinary field reassignment.

For `Notice("build","ready")`, rendering and the delivery return value are `"[build] ready"`. Empty text gives `"[build] "`. Two deliveries preserve order. Sending through one MemorySender leaves another instance unchanged.

The protocol supports static structural checking. Runtime checks here validate Notice values and the send capability; they do not prove an arbitrary collaborator's complete signature or behavior.

## Work and evidence

Predict the demonstration, complete the two bodies, then run the five contracts. Use a separate sender class to show that inheritance from MemorySender is unnecessary. Record one failure and explain which boundary reports it.

The completed demonstration prints:

```text
rendered: [build] ready
first: ['[build] ready', '[build] ']
second: ['[build] ready']
```

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

In the site IDE, confirm the import, edit and save, then export all four files for the native tests and checker. The IDE runs its bundled Python interpreter; record its version separately from native CPython 3.14.

[Protocol documentation](https://docs.python.org/3.14/library/typing.html#typing.Protocol)
