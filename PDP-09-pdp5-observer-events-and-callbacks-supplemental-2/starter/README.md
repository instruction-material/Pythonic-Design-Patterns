# Snapshot Event Fan-Out: starter

Implement only the named learner bodies: subscribe, publish_snapshot. The remaining model, driver and tests are supplied.

Event(topic, value) is frozen. topic is a nonblank string; value is a nonnegative integer, excluding bool. subscribe appends one callable and permits duplicates. publish_snapshot validates the event and every captured callable before delivery, then calls the captured tuple in order. Removing a listener during delivery still permits its captured call; adding one affects only later publications. The first listener error propagates unchanged and stops later callbacks; there is no retry. Callbacks return None. An empty listener list is valid.

Complete only subscribe and publish_snapshot. Preserve Event, the callback signature, the driver and the supplied tests. Verify a zero-valued event, duplicate callbacks, mutation during publication, original exception identity, invalid payloads and a non-None callback result. The exercise isolates snapshot fan-out from the larger event bus.

Run from this role folder with Python 3.14:

```sh
python3.14 -B main.py
python3.14 -B -m unittest discover -s . -p test_contract.py -v
```

Reference driver output:

```text
delivery: ['order:3', 'audit:3']
```

Development typing uses the exact requirements-dev.txt pins and a separate virtual environment. Runtime demonstrations and public contracts use the standard library. The repository verification script runs fresh strict checks.
