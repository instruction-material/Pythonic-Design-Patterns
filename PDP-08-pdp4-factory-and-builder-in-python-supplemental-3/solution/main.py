"""Select a unique provider before invoking any third-party loader."""
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import cast

TextProvider = Callable[[str], str]


@dataclass(frozen=True)
class ProviderSpec:
    name: str
    loader: Callable[[], object]

    def __post_init__(self) -> None:
        if not isinstance(self.name, str):
            raise TypeError("provider name must be a string")
        if not self.name.strip():
            raise ValueError("provider name must contain a non-space character")
        if not callable(self.loader):
            raise TypeError("provider loader must be callable")


class ProviderLoadError(RuntimeError):
    """A selected provider failed to load; its original cause is retained."""


def select_provider(name: str, providers: Iterable[ProviderSpec]) -> ProviderSpec:
    """Read candidates once and require exactly one exact-name match."""
    if not isinstance(name, str):
        raise TypeError("name must be a string")
    if not name.strip():
        raise ValueError("name must contain a non-space character")
    matches: list[ProviderSpec] = []
    for provider in providers:
        if not isinstance(provider, ProviderSpec):
            raise TypeError("each candidate must be a ProviderSpec")
        if provider.name == name:
            matches.append(provider)
    if not matches:
        raise LookupError(name)
    if len(matches) != 1:
        raise ValueError("duplicate provider name")
    return matches[0]


def load_provider(name: str, providers: Iterable[ProviderSpec]) -> TextProvider:
    """Load once; runtime checks establish callability, not a full signature."""
    selected = select_provider(name, providers)
    try:
        loaded = selected.loader()
    except Exception as error:
        raise ProviderLoadError(name) from error
    if not callable(loaded):
        raise TypeError("loaded provider must be callable")
    return cast(TextProvider, loaded)


def bracket(text: str) -> str:
    return "[" + text + "]"


def main() -> None:
    try:
        candidates = [ProviderSpec("bracket", lambda: bracket)]
        provider = load_provider("bracket", candidates)
        print("loaded:", provider("ready"))
    except NotImplementedError as error:
        print("PDP4 starter unfinished:", error)


if __name__ == "__main__":
    main()
