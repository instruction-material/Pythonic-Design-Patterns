# ExitStack Resource Lifecycle: solution

This reference preserves the same public contract and demonstrates the documented implementation choice.

managed_resource(name, trace, *, fail_acquire=False, suppress=False) is a contextmanager factory. Each factory call creates a fresh single-use manager. It records acquire:name; an acquisition failure records failed:name and raises OSError before yielding. A successful acquisition yields the name and always records release:name on exit. It suppresses only ValueError when suppress=True, recording suppressed:name first. Other exceptions propagate.

run_resources(names, trace, *, fail_at=None, fail_body=False, suppress_at=None) validates all names before acquisition and uses ExitStack for a data-driven resource count. Enter in list order; release in reverse order. Append body after all acquisitions. Return complete on ordinary completion or suppressed when a selected manager suppresses the simulated body ValueError. Unhandled body/acquisition errors propagate after cleanup. The failing acquisition is not released because it never yielded an acquired resource.

Complete only managed_resource and run_resources. Preserve decorators, signatures, the driver and tests. Check zero resources, normal completion, halfway acquisition failure, body failure, selected suppression, fresh repeated managers and nested managers. The trace models real context-manager enter/exit semantics without opening external resources.

Run from this role folder with Python 3.14:

```sh
python3.14 -B main.py
python3.14 -B -m unittest discover -s . -p test_contract.py -v
```

Reference driver output:

```text
result: complete
trace: ['acquire:profile', 'acquire:billing', 'body', 'release:billing', 'release:profile']
```

Development typing uses the exact requirements-dev.txt pins and a separate virtual environment. Runtime demonstrations and public contracts use the standard library. The repository verification script runs fresh strict checks.
