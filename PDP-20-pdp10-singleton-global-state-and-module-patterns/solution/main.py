"""Request context and an explicitly resettable process cache have different owners."""
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar, copy_context

_REQUEST_ID: ContextVar[str | None] = ContextVar("request_id", default=None)
_PROCESS_CACHE: dict[str, str] = {}


def text(value: object) -> str:
    if not isinstance(value, str):
        raise TypeError("value must be text")
    if not value:
        raise ValueError("value must be nonempty")
    return value


@contextmanager
def request_context(name: str) -> Iterator[str]:
    text(name)
    token = _REQUEST_ID.set(name)
    try:
        yield name
    finally:
        _REQUEST_ID.reset(token)


def current_request() -> str:
    value = _REQUEST_ID.get()
    if value is None:
        raise LookupError("no request context")
    return value


def remember(key: str, value: str) -> str:
    text(key)
    text(value)
    return _PROCESS_CACHE.setdefault(key, value)


def cache_snapshot() -> dict[str, str]:
    return dict(_PROCESS_CACHE)


def clear_cache() -> None:
    _PROCESS_CACHE.clear()


def main() -> None:
    clear_cache()
    try:
        with request_context("outer"):
            copied = copy_context()
            with request_context("inner"):
                print("inside:", current_request())
            print("restored:", current_request())
        print("copied:", copied.run(current_request))
        print("cached:", remember("host", "first"), remember("host", "second"))
    finally:
        clear_cache()
    print("cache after shutdown:", cache_snapshot())


if __name__ == "__main__":
    try:
        main()
    except NotImplementedError as error:
        print("starter unfinished:", error)
