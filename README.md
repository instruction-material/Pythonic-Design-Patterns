# Pythonic Design Patterns

Course-owned learner and reference files for Python-specific design judgment and refactoring.

The two opening callable labs have complete in-folder briefs, learner contract tests, unfinished scaffolds and runnable references:

- PDP-01: function, configured closure and callable-object comparison.
- PDP-02: named callable registry and explicit boundary errors.

Each imported starter includes its own README, main.py, test_contract.py and requirements-dev.txt. Complete the named bodies, run the local contract tests, then compare the reference. The programs use the standard library; pinned development requirements provide static type checking.

## Native setup and verification

Use CPython 3.14. From this repository root on macOS/Linux:

```sh
python3.14 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
COURSE_PYTHON=.venv/bin/python ./verify-course-source.sh
```

On Windows, create the environment with `py -3.14 -m venv .venv` and use `.venv\Scripts\python.exe` for the Python commands. Run unit tests with `-B -m unittest discover -s tests -v` and type-check each opening main.py with `-m mypy --strict --python-version 3.14`.

The repository gate verifies source inventory plus the repaired opening scope: thirteen maintainer tests, both completed learner fixtures and strict type checks of four starter/reference programs. In-folder five-test contracts are learner checks; repository tests also check pristine scaffolds and are maintainer checks.

## Remaining review

Twenty-two generated formatter pairs and seven larger pattern projects remain in the course audit. A passing opening gate establishes the opening scope. SOURCE_BACKLOG.md tracks the other sources and whole-course work.
