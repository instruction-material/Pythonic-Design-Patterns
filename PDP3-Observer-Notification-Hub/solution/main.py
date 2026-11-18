"""Order-event publication with explicit lifetime and delivery policies."""
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
import inspect
from types import TracebackType
from typing import Protocol, cast
from weakref import WeakMethod

ORDER_UPDATED_EVENT = "order.updated"
Listener = Callable[["OrderEvent"], None]
AsyncListener = Callable[["OrderEvent"], Awaitable[None]]


def require_text(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError("event text must be a string")
    if not value.strip():
        raise ValueError("event text must contain a non-space character")
    return value


@dataclass(frozen=True)
class OrderEvent:
    order_id: str
    status: str
    customer_email: str

    def __post_init__(self) -> None:
        for value in (self.order_id, self.status, self.customer_email):
            require_text(value)


class Disconnectable(Protocol):
    def unsubscribe(self, event_name: str, token: int) -> None: ...


class Subscription:
    """An owned, idempotent connection; entering never reconnects it."""
    def __init__(self, bus: Disconnectable, event_name: str, token: int) -> None:
        self._bus, self._event_name, self.token = bus, event_name, token
        self._closed = False

    def close(self) -> None:
        if not self._closed:
            self._bus.unsubscribe(self._event_name, self.token)
            self._closed = True

    def __enter__(self) -> "Subscription":
        return self

    def __exit__(self, exc_type: type[BaseException] | None,
                 exc: BaseException | None, tb: TracebackType | None) -> None:
        self.close()


@dataclass
class _Slot:
    token: int
    resolve: Callable[[], Listener | None]


def _resolver(callback: Listener, weak: bool) -> Callable[[], Listener | None]:
    if not callable(callback):
        raise TypeError("listener must be callable")
    if not isinstance(weak, bool):
        raise TypeError("weak must be a bool")
    if inspect.iscoroutinefunction(callback) or inspect.iscoroutinefunction(
        getattr(callback, "__call__", None)
    ):
        raise TypeError("use AsyncEventBus for coroutine listeners")
    if weak:
        # WeakMethod retains the owner/function relationship, not a temporary
        # bound-method object. The returned resolver does not capture callback.
        ref = WeakMethod(callback)
        return lambda: ref()
    return lambda: callback


def _invoke(callback: Listener, event: OrderEvent) -> None:
    result = cast(Callable[[OrderEvent], object], callback)(event)
    if inspect.iscoroutine(result):
        result.close()
    if result is not None:
        raise TypeError("a synchronous listener must return None")


def _event(event: OrderEvent) -> None:
    if not isinstance(event, OrderEvent):
        raise TypeError("event must be an OrderEvent")


class _Registry:
    """Own connection storage, token identity and weak-listener cleanup."""
    def __init__(self) -> None:
        self._listeners: dict[str, dict[int, Callable[[], Listener | None]]] = {}
        self._next_token = 1

    def add(self, event_name: str, listener: Listener, weak: bool) -> int:
        resolve = _resolver(listener, weak)
        token = self._next_token
        self._next_token += 1
        self._listeners.setdefault(event_name, {})[token] = resolve
        return token

    def remove(self, event_name: str, token: int) -> None:
        self._listeners.get(event_name, {}).pop(token, None)

    def snapshot(self, event_name: str) -> tuple[Listener, ...]:
        callbacks: list[Listener] = []
        for token, resolve in tuple(self._listeners.get(event_name, {}).items()):
            callback = resolve()
            if callback is None:
                self.remove(event_name, token)
            else:
                callbacks.append(callback)
        return tuple(callbacks)

    def clear(self) -> None:
        self._listeners.clear()


class EventBus:
    """The same public behavior with storage owned by a separate registry."""
    def __init__(self) -> None:
        self._registry = _Registry()
        self._closed = False

    def subscribe(self, event_name: str, listener: Listener, *, weak: bool = False) -> int:
        require_text(event_name)
        if self._closed:
            raise RuntimeError("event bus is closed")
        return self._registry.add(event_name, listener, weak)

    def unsubscribe(self, event_name: str, token: int) -> None:
        self._registry.remove(event_name, token)

    def connect(self, event_name: str, listener: Listener, *, weak: bool = False) -> Subscription:
        return Subscription(self, event_name, self.subscribe(event_name, listener, weak=weak))

    def publish(self, event_name: str, event: OrderEvent) -> None:
        require_text(event_name)
        _event(event)
        if self._closed:
            raise RuntimeError("event bus is closed")
        for callback in self._registry.snapshot(event_name):
            _invoke(callback, event)

    def close(self) -> None:
        self._registry.clear()
        self._closed = True


class AsyncEventBus:
    """Serial awaited delivery; overlapping/nested publications are rejected.

    This bus creates zero tasks. The caller owns the publication task, if one
    is created, and cancels/awaits it before closing the idle bus.
    """
    def __init__(self) -> None:
        self._listeners: dict[str, dict[int, AsyncListener]] = {}
        self._next_token = 1
        self._publishing = False
        self._closed = False

    def subscribe(self, event_name: str, listener: AsyncListener) -> int:
        require_text(event_name)
        if self._closed:
            raise RuntimeError("event bus is closed")
        if not callable(listener):
            raise TypeError("listener must be callable")
        token = self._next_token
        self._next_token += 1
        self._listeners.setdefault(event_name, {})[token] = listener
        return token

    def unsubscribe(self, event_name: str, token: int) -> None:
        self._listeners.get(event_name, {}).pop(token, None)

    def connect(self, event_name: str, listener: AsyncListener) -> Subscription:
        return Subscription(self, event_name, self.subscribe(event_name, listener))

    async def publish(self, event_name: str, event: OrderEvent) -> None:
        require_text(event_name)
        _event(event)
        if self._closed:
            raise RuntimeError("event bus is closed")
        if self._publishing:
            raise RuntimeError("one publication may be in flight")
        snapshot = tuple(self._listeners.get(event_name, {}).values())
        self._publishing = True
        try:
            for callback in snapshot:
                pending = cast(Callable[[OrderEvent], Awaitable[object]], callback)(event)
                if not inspect.isawaitable(pending):
                    raise TypeError("async listener must return an awaitable")
                result = await pending
                if result is not None:
                    raise TypeError("an async listener must return None")
        finally:
            self._publishing = False

    def close(self) -> None:
        if self._publishing:
            raise RuntimeError("cancel and await the publication before close")
        self._listeners.clear()
        self._closed = True


def print_summary(event: OrderEvent) -> None:
    print(f"summary: {event.order_id} -> {event.status}")


def print_email(event: OrderEvent) -> None:
    print(f"email: sent {event.status} message to {event.customer_email}")


def audit_log(event: OrderEvent) -> None:
    print(f"audit: order={event.order_id} status={event.status}")


def build_order_event(status: str) -> OrderEvent:
    return OrderEvent("A-102", status, "ada@example.com")


def main() -> None:
    bus = EventBus()
    summary_token = bus.subscribe(ORDER_UPDATED_EVENT, print_summary)
    bus.subscribe(ORDER_UPDATED_EVENT, print_email)
    bus.subscribe(ORDER_UPDATED_EVENT, audit_log)
    bus.publish(ORDER_UPDATED_EVENT, build_order_event("shipped"))
    bus.unsubscribe(ORDER_UPDATED_EVENT, summary_token)
    bus.publish(ORDER_UPDATED_EVENT, build_order_event("delivered"))
    bus.close()


if __name__ == "__main__":
    main()
