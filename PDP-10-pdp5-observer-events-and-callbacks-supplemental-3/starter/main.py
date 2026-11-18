"""Own a listener connection with an idempotent context-manager handle."""
from collections.abc import Callable
from types import TracebackType
from typing import cast
import inspect
Listener = Callable[[str], None]

class Registry:

    def __init__(self) -> None:
        self.listeners: dict[int, Listener] = {}
        self._next_token = 1

    def connect(self, callback: Listener) -> 'Connection':
        if not callable(callback):
            raise TypeError('listener must be callable')
        token = self._next_token
        self._next_token += 1
        self.listeners[token] = callback
        return Connection(self, token)

class Connection:

    def __init__(self, registry: Registry, token: int) -> None:
        self._registry, self.token = (registry, token)
        self._closed = False

    def close(self) -> None:
        raise NotImplementedError('Complete close.')

    def __enter__(self) -> 'Connection':
        return self

    def __exit__(self, exc_type: type[BaseException] | None, exc: BaseException | None, tb: TracebackType | None) -> None:
        self.close()

def deliver(registry: Registry, text: str) -> None:
    raise NotImplementedError('Complete deliver.')

def main() -> None:
    seen: list[str] = []
    registry = Registry()
    try:
        with registry.connect(seen.append) as connection:
            deliver(registry, 'ready')
            print('inside:', seen)
        deliver(registry, 'later')
        connection.close()
        print('after:', seen)
    except NotImplementedError:
        print('PDP5 starter unfinished: Complete close and deliver.')
if __name__ == '__main__':
    main()
