# Strategy Rulebook: Learner baseline

A working pricing baseline for a behavior-preserving Strategy refactor.

The starter already runs and passes the contract. Preserve behavior while changing the representation; compare the reference after a green refactor.

## Required behavior

Keep the public LineItem, subtotal, standard_total, loyalty_total, bulk_total, register_rule, build_rulebook and checkout_total interfaces. The optional third checkout argument supplies a rulebook; the legacy two-argument call still uses RULES. The sample cart has subtotal49.50, loyalty44.55 and bulk41.50.

Line names contain a non-space character; prices are finite nonnegative numbers; quantities are nonnegative integers, with booleans rejected. The default bulk discount applies at six items and floors the result at zero. Every checkout passes a separate list of frozen line values to one selected rule, validates its finite nonnegative result and rounds once to two places using Python round. A missing name raises KeyError; duplicate registration raises ValueError before mutation. A rule exception propagates without retry.

This is a finite-float teaching model, with Python's binary-float rounding behavior. It is not a production currency policy.

Core: refactor the function-based baseline into configured callable objects while preserving the contract and sample results. Optional Rulebook: supply two independent custom registries and add a new rule without modifying checkout_total; show duplicate-name and unknown-selection outcomes. Keep the new rule separate from the behavior-preserving core transformation.

## Run and check

Use CPython 3.14 for native checks. From this imported folder:

~~~sh
python main.py
python -B -m unittest discover -s . -p test_contract.py -v
python -m mypy --strict --no-incremental --python-version 3.14 main.py
~~~

The program uses only the standard library. The included requirements-dev.txt pins the optional native checker and its tools. Install it in a virtual environment before the checker command; see the repository setup guide for platform-specific commands.

## Complete driver output

~~~text
standard: $49.50
loyalty: $44.55
bulk: $41.50
~~~

The supplied contract suite checks the normal case, meaningful boundaries and independent state/error behavior. Keep a short decision record explaining the chosen representation and one limitation.
