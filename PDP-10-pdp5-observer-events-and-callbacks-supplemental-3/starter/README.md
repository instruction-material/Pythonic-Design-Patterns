# Owned Subscription Lifetime: starter

Implement only the named learner bodies: close, deliver. The remaining model, driver and tests are supplied.

Registry.connect registers a Callable[[str], None] under a fresh token and returns a Connection. Each duplicate registration has its own token. close removes only that connection and is idempotent. Connection.__exit__ calls close on success and exception paths; it returns None so the body exception propagates. Entering a closed handle does not reconnect.

deliver captures the current ordered callbacks once. Closing a handle during a publication changes later publications; its already captured callback still runs. Empty text is valid; non-string text raises TypeError before delivery. The first callback error stops delivery without retry; callbacks return None.

Complete only Connection.close and deliver. Preserve token creation, the context-manager entry/exit methods, the driver and the public tests. Compare normal exit, exceptional exit, duplicate handles, repeated close and removal during delivery.

Run from this role folder with Python 3.14:

```sh
python3.14 -B main.py
python3.14 -B -m unittest discover -s . -p test_contract.py -v
```

Reference driver output:

```text
inside: ['ready']
after: ['ready']
```

Development typing uses the exact requirements-dev.txt pins and a separate virtual environment. Runtime demonstrations and public contracts use the standard library. The repository verification script runs fresh strict checks.
