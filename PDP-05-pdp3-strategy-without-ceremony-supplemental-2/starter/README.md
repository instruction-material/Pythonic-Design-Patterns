# Configured Score Callables: Learner baseline

Transfer Strategy to integer scores.

Complete only run_rule, make_bonus_rule. The pristine starter announces its unfinished state; the reference passes all contracts.

## Required behavior

Scores and bonus amounts are nonnegative integers; booleans and non-integers raise TypeError and negatives raise ValueError. run_rule calls one callable exactly once, validates its returned score and propagates its exception. make_bonus_rule captures one fixed bonus and returns a rule; repeated calls with the same input return the same result. Distinct returned rules retain independent configuration. Preserve the supplied driver and validators.

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
doubled: 8
bonus: 7
repeat: 7
~~~

The supplied contract suite checks the normal case, meaningful boundaries and independent state/error behavior. Keep a short decision record explaining the chosen representation and one limitation.
