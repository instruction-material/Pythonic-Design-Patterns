# Decorator, Proxy and Facade Toolkit: starter

This is a complete runnable refactoring baseline. Run its contracts before changing structure.

log_calls preserves names, documentation, annotations, __wrapped__, and positional/keyword calls. A synchronous wrapper logs when called; a coroutine wrapper logs when awaited; generator wrappers log on first advancement. It preserves coroutine/generator function shape. Generator send, throw, completion values and close are delegated; asynchronous generators preserve asend, athrow, completion and aclose. Exceptions propagate unchanged and owned generator cleanup runs on close/cancellation. The public tests exercise all four shapes with standard Python 3.14 and an owned event loop.

cache_result accepts synchronous value functions. Coroutine/generator functions are rejected; dynamically returned deferred computations raise TypeError instead of being cached. The key binds arguments against the original signature, applies defaults and sorts variable keyword items. Bound values must be hashable: a list argument raises TypeError before the core executes. Equivalent positional/keyword/default calls share a key. Successful values are cached by identity, so a generic cached mutable object is shared. Exceptions are never cached. clear_cache invalidates the cache. One reentrant lock protects lookup, computation and invalidation, serializing simultaneous misses; this deliberately serializes computations for different keys too.

ProfileService returns a supplied profile with username, plan=pro and status=active. Its loads count records actual loads. AuthorizationProxy owns a copy of the initial allowlist and rechecks its current allowed_users before every cache lookup, including hits. Policy changes are made between calls by the client. Both the initial service dictionary and each returned dictionary are copied, protecting cached profile snapshots from core/caller edits. invalidate clears those snapshots. This is a local classroom authorization model, without account authentication or network requests.

ProfileFacade calls the authorized profile reader before billing, then returns 'ada -> plan=pro status=active billing=paid' for the sample data. A denied profile skips billing. The optional billing dependency defaults to the supplied BillingService, preserving the one-argument construction form. Independent conforming readers can be passed in.

Core refactor: preserve the green public contracts while replacing AuthorizationProxy's explicit dictionary memoization with a composed cache_result delegate. Keep authorization outside that delegate and keep copying at both dictionary boundaries. The reference demonstrates that separation. The generic decorator remains independently tested, including wrapper order and concurrent misses.

Optional client: implement a changing supplied profile reader, load ada twice, edit the returned dictionary and confirm the cache remains unchanged. Revoke ada and confirm a cached result is denied. Change the core plan, restore access, invalidate and load again. The underlying loads count is 1 before invalidation and 2 afterward; the new plan appears only after invalidation. The solution brief supplies a full client. This exercises policy and freshness rather than repeating the core refactor.

Run from this role folder with Python 3.14:

```sh
python3.14 -B main.py
python3.14 -B -m unittest discover -s . -p test_contract.py -v
```

Reference driver output:

```text
log: calling get_profile
ada -> plan=pro status=active billing=paid
ada -> plan=pro status=active billing=paid
```

Development typing uses the exact requirements-dev.txt pins and a separate virtual environment. Runtime demonstrations and public contracts use the standard library. The repository verification script runs fresh strict checks.
