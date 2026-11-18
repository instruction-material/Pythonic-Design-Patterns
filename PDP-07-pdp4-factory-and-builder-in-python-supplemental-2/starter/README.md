# Immutable Report Construction: Learner baseline

Compare named construction functions with a mutable builder.

Complete only add_section, render_text. The pristine starter announces its unfinished state; the reference passes all contracts.

## Required behavior

Config is a frozen data class with a nonblank title, an ordered tuple of nonblank section strings and a boolean footer flag. add_section returns a fresh Config with the section appended, preserving the original value. render_text returns the uppercase title, ordered sections and optional -- end -- line joined by newline, with no trailing newline. Preserve exact section whitespace and duplicate sections; validation rejects blank text rather than silently trimming it. An object of the wrong type raises TypeError. Explain why this small immutable value does not require a builder.

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
base sections: 0
PLAN
draft
reviewed
~~~

The supplied contract suite checks the normal case, meaningful boundaries and independent state/error behavior. Keep a short decision record explaining the chosen representation and one limitation.
