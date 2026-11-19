# Bounded Editor Undo

Python 3.14. Store the previous immutable text on every replacement and retain only the newest limit entries. Undo is LIFO, returns False for an empty history, and restores the previous text exactly, including repeated and empty edits. Each document owns its own history. The oldest discarded state is outside the undo window.

Complete only apply_edit, undo_edit. The supplied driver catches the declared unfinished work.

Run `python3.14 -B main.py` and `python3.14 -B -m unittest discover -s . -p test_contract.py -v`. After completion, the driver output is:

```text
edited: third
undo: second
undo: first
empty: False
```

The contract suite has five behavioral groups. Development pins are installed with `python3.14 -m pip install -r requirements-dev.txt`; runtime code uses the standard library.
