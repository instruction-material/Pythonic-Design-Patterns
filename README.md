# Pythonic Design Patterns

Course-owned learner/reference files for Python-specific design judgment and refactoring.

Sixteen source families have complete role briefs, contracts and native checking:
- PDP-01/PDP-02: callable comparison and named formatter registry.
- PDP-03/PDP-04: composed notice delivery and owned records/snapshots.
- PDP-05/PDP-06: configured score callables and deterministic strategy comparison.
- PDP-07/PDP-08: immutable report construction and provider loading boundaries.
- PDP-09/PDP-10: snapshot event fan-out and owned subscription lifetime.
- PDP-11/PDP-12: transparent tracing and ExitStack resource lifecycle.
- Observer Notification Hub and Wrapper Toolkit: complete behavior-preserving baselines, separate optional clients, weak listeners, controlled async delivery, transparent deferred calls and owned cached profiles.
- Strategy Rulebook and Factory/Builder Config Kit: working baselines for behavior-preserving refactors, with separately defined optional work.

Each imported role contains README.md, main.py, test_contract.py and requirements-dev.txt. Small scaffolds declare named unfinished bodies; the two larger refactoring starters already run and pass their public contracts. Preserve the appropriate role.

## Native setup

Use CPython 3.14. On macOS/Linux:
~~~sh
python3.14 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
COURSE_PYTHON=.venv/bin/python ./verify-course-source.sh
~~~

On Windows, create the environment with py -3.14 -m venv .venv and use .venv\Scripts\python.exe for Python commands. Run the repository unittest suite and fresh strict checks for the same thirty-two qualified main.py files.

The native gate passes 24 maintainer tests, 54 reference contract cases, 14 working-baseline cases, 40 completed-scaffold cases and fresh strict checks of 20 programs. The maintained positive/negative protocol probes use isolated caches and fresh checking.

## Remaining review

Twelve duplicate generated pairs and three larger pattern packs remain under review. The active catalog retains 31 source families. Site teaching, actual IDE workflows and full-course acceptance have separate evidence; the native gate accepts the sixteen named families only.
