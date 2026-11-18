# Transparent Wrapper Order: starter

Implement only the named learner bodies: make_traced, compose_layers. The remaining model, driver and tests are supplied.

make_traced(label, trace, func) wraps a synchronous value function with a before entry and a finally-protected after entry. Preserve functools.wraps metadata, signature inspection, __wrapped__, arguments, return identity and original exceptions. A label is a nonblank string. This focused exercise rejects deferred function shapes; the larger Toolkit demonstrates coroutine and generator adapters.

compose_layers(func, labels, trace) reads labels once. The first listed label is the outermost wrapper: ['audit', 'metrics'] yields audit:before, metrics:before, metrics:after, audit:after. An empty list returns the original callable; duplicate labels remain separate layers. Validate all labels before wrapping. Calling __wrapped__ isolates the next layer; walking the chain reaches the core.

Complete only make_traced and compose_layers. Keep the sample calculate(value, *, offset=1), metadata, driver and tests. Test success, core failure, empty/duplicate layers and invalid labels without converting exceptions to fallback results.

Run from this role folder with Python 3.14:

```sh
python3.14 -B main.py
python3.14 -B -m unittest discover -s . -p test_contract.py -v
```

Reference driver output:

```text
result: 9
trace: ['audit:before', 'metrics:before', 'metrics:after', 'audit:after']
```

Development typing uses the exact requirements-dev.txt pins and a separate virtual environment. Runtime demonstrations and public contracts use the standard library. The repository verification script runs fresh strict checks.
