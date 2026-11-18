# Observer Notification Hub: starter

This is a complete runnable refactoring baseline. Run its contracts before changing structure.

OrderEvent(order_id, status, customer_email) is frozen; all three fields and the channel name are nonblank strings. Callbacks accept that event and return None. Notifications are printed classroom data; the email callback does not send mail.

EventBus.subscribe returns a distinct integer token for each registration, including duplicate callbacks. unsubscribe removes just that token and is idempotent for an unknown token. connect returns an owned Subscription with close and a with boundary. Re-entering a closed handle leaves it closed. The default strong connection retains its owner until disconnect. weak=True uses WeakMethod for a Python bound method; expired methods are pruned. A listener resolved as live at snapshot time remains alive for that captured delivery.

One synchronous publication captures ordered callbacks once. A removal affects the next publication; an addition waits for the next publication. Nested publications run immediately with their own snapshots, so the order for callbacks a and b is a:outer, a:inner, b:inner, b:outer. The first listener exception stops delivery and propagates unchanged. Each listener runs once per snapshot, without retry. Closing the bus prevents new publication/registration and clears stored connections.

AsyncEventBus uses the same ordered snapshot and fail-fast policy with serial awaited callbacks. It creates zero tasks. Overlapping or nested async publication raises RuntimeError; this single-publication capacity is the backpressure policy. Cancellation propagates to the active listener and later listeners remain unstarted. The caller cancels and awaits any caller-created publication task before closing the idle bus; close rejects an active publication. Async connections retain their listener strongly and use explicit disconnection. Run the async public tests with standard Python 3.14, where IsolatedAsyncioTestCase owns the event loop. The default main.py demonstration is synchronous and runs in the site IDE.

Core refactor: keep the entire public API and both delivery policies while moving synchronous listener storage/token allocation/snapshot cleanup from EventBus into a private registry. The starter is already correct and runnable. The reference demonstrates the extracted registry. Preserve all fifteen public contracts before and after the change.

Optional client: add client.py with three supplied updates: A-102 shipped, B-205 packed, A-102 delivered. Keep an audit listener for all three. Own a temporary dashboard connection only around the first two publications. The audit receives three entries; dashboard receives the first two and no delivered update. Close the dashboard twice to verify idempotence. The solution brief supplies a complete comparison client. This client task changes composition and lifetime; the core refactor changes implementation structure.

Run from this role folder with Python 3.14:

```sh
python3.14 -B main.py
python3.14 -B -m unittest discover -s . -p test_contract.py -v
```

Reference driver output:

```text
summary: A-102 -> shipped
email: sent shipped message to ada@example.com
audit: order=A-102 status=shipped
email: sent delivered message to ada@example.com
audit: order=A-102 status=delivered
```

Development typing uses the exact requirements-dev.txt pins and a separate virtual environment. Runtime demonstrations and public contracts use the standard library. The repository verification script runs fresh strict checks.
