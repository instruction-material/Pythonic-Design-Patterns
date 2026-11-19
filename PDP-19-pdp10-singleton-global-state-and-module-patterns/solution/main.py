"""Application-owned services with explicit configuration and shutdown."""
from collections.abc import Callable
from dataclasses import dataclass
from types import TracebackType
from typing import Protocol


@dataclass(frozen=True)
class Config:
    prefix: str

    def __post_init__(self) -> None:
        if not isinstance(self.prefix, str):
            raise TypeError("prefix must be text")
        if not self.prefix:
            raise ValueError("prefix must be nonempty")


class Store(Protocol):
    def save(self, text: str) -> None: ...
    def close(self) -> None: ...


class MemoryStore:
    def __init__(self) -> None:
        self._messages: list[str] = []
        self.closed = False

    @property
    def messages(self) -> tuple[str, ...]:
        return tuple(self._messages)

    def save(self, text: str) -> None:
        if self.closed:
            raise RuntimeError("store is closed")
        self._messages.append(text)

    def close(self) -> None:
        self.closed = True


class Application:
    def __init__(self, config: Config, store: Store) -> None:
        self.config = config
        self.store = store
        self.closed = False

    def run(self, text: str) -> str:
        if self.closed:
            raise RuntimeError("application is closed")
        if not isinstance(text, str):
            raise TypeError("message must be text")
        result = self.config.prefix + text.strip()
        self.store.save(result)
        return result

    def close(self) -> None:
        if not self.closed:
            self.closed = True
            self.store.close()

    def __enter__(self) -> "Application":
        if self.closed:
            raise RuntimeError("application is closed")
        return self

    def __exit__(self, exc_type: type[BaseException] | None,
                 exc: BaseException | None, tb: TracebackType | None) -> None:
        self.close()


def create_application(config: Config, factory: Callable[[], Store] = MemoryStore) -> Application:
    if not isinstance(config, Config):
        raise TypeError("config must be Config")
    if not callable(factory):
        raise TypeError("store factory must be callable")
    store = factory()
    if not callable(getattr(store, "save", None)) or not callable(getattr(store, "close", None)):
        raise TypeError("store must provide save and close")
    return Application(config, store)


def main() -> None:
    first = MemoryStore()
    second = MemoryStore()
    with create_application(Config("A:"), lambda: first) as app:
        print("first:", app.run(" hello "))
    with create_application(Config("B:"), lambda: second) as app:
        print("second:", app.run(" world "))
    print("independent:", first.messages, second.messages)
    print("closed:", first.closed, second.closed)


if __name__ == "__main__":
    try:
        main()
    except NotImplementedError as error:
        print("starter unfinished:", error)
