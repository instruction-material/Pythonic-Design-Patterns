# Injected Vendor Boundary

Python 3.14. Call an injected zero-argument reader exactly once. Translate {values:[integers]} into an owned immutable tuple; missing values defaults to an empty list, extra fields are ignored, bool/float values are rejected. Wrap reader OSError/TimeoutError as SourceError with the original cause. Preserve programming exceptions. Compute a maximum for nonempty data and raise ValueError for empty data. Use local readers without network access.

Complete only fetch_values, highest_value. The supplied driver catches the declared unfinished work.

Run `python3.14 -B main.py` and `python3.14 -B -m unittest discover -s . -p test_contract.py -v`. After completion, the driver output is:

```text
highest: 9
source failure: TimeoutError
```

The contract suite has five behavioral groups. Development pins are installed with `python3.14 -m pip install -r requirements-dev.txt`; runtime code uses the standard library.
