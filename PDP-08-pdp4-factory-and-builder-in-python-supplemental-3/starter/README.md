# Provider Discovery Boundary: Learner baseline

Exercise plugin selection with supplied offline candidates.

Complete only select_provider, load_provider. The pristine starter announces its unfinished state; the reference passes all contracts.

## Required behavior

ProviderSpec holds a nonblank exact name and callable loader. select_provider reads a finite iterable once and requires one exact-name match: no match raises LookupError; duplicate matches raise ValueError. Validate all yielded candidates. Resolve this uniqueness check before loading anything. load_provider invokes only the selected loader, once. Its failure becomes ProviderLoadError with the original exception as __cause__; no retries or fallback providers run. A non-callable loaded value raises TypeError.

The runtime boundary establishes callability; it cannot prove the callable's complete signature or return contract. A callable with the wrong signature can load successfully and fail when invoked. Static typing checks known code; installed plugin code remains an external boundary. The supplied fake candidates require no installed plugin, network or account. The matching course reading maps this policy to importlib.metadata entry points.

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
loaded: [ready]
~~~

The supplied contract suite checks the normal case, meaningful boundaries and independent state/error behavior. Keep a short decision record explaining the chosen representation and one limitation.
