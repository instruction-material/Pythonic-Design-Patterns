# PDP9 comparison clients

The original main.py, README.md and public adapter tests remain the PDP8 baseline. PDP9 uses pdp9_comparison.py to compare class/callable equivalence and a score-preserving extension, then pdp9_failure_client.py for ordered short-circuit behavior and exception identity.

With Python 3.14, run `python -B pdp9_comparison.py` and `python -B pdp9_failure_client.py` from this exported folder. In a single-entry site console, append the client definitions/calls after the imported main definitions, removing only its `from main import ...` statement. Retain all imported files when saving/exporting.

Expected comparison output: csv forms equal True; webhook forms equal True; replacement scores [7, 9]; replacement equal True. Expected failure output for each form: same failure True and events ['adapt:first', 'transform:first', 'adapt:second', 'transform:second']. The third record is never visited. Earlier callback effects remain.

Keep the original ten contract groups green. Add empty, generator, adapter-error and stateful-callable cases as described in the corresponding course brief. The source schema and immutable Lead boundary remain unchanged.
