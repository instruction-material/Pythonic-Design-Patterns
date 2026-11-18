# Captured Callable Queue

Python 3.14. Capture the amount from the configuration when creating each callable. Execute the captured queue in order using a local integer accumulator. Later configuration or queue-list changes must not alter already captured values or membership. Validate the full queue before calling it; preserve the first callback exception. Callbacks may have external effects, which this local accumulator cannot reverse.

Complete only make_increment, run_queue. The supplied driver catches the declared unfinished work.

Run `python3.14 -B main.py` and `python3.14 -B -m unittest discover -s . -p test_contract.py -v`. After completion, the driver output is:

```text
result: 9
config now: 100
```

The contract suite has five behavioral groups. Development pins are installed with `python3.14 -m pip install -r requirements-dev.txt`; runtime code uses the standard library.
