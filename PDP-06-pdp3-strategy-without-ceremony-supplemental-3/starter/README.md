# Compare Named Score Rules: Learner baseline

Choose a strategy by observed output with a deterministic tie policy.

Complete only register_score_rule, choose_best. The pristine starter announces its unfinished state; the reference passes all contracts.

## Required behavior

Registration validates a nonblank exact string name and callable before changing a dictionary. Reject duplicate names with ValueError and preserve the old binding. choose_best requires a valid nonnegative integer score and a nonempty mapping. Validate the captured names and callable capabilities before invoking rules. Capture binding order once, call each captured rule once and choose the greatest valid score; equal results keep the first binding. A callback may mutate the original mapping, but the captured bindings still run. Invalid scores/results fail as in the score-callable lab. A rule exception propagates immediately, leaving later rules uncalled. Empty mappings raise ValueError.

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
winner: bonus 9
rules: ['double', 'bonus']
~~~

The supplied contract suite checks the normal case, meaningful boundaries and independent state/error behavior. Keep a short decision record explaining the chosen representation and one limitation.
