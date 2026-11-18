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
            raise TypeError('provider name must be a string')
        if not self.name.strip():
            raise ValueError('provider name must contain a non-space character')
        if not callable(self.loader):
            raise TypeError('provider loader must be callable')

class ProviderLoadError(RuntimeError):
    """A selected provider failed to load; its original cause is retained."""

def select_provider(name: str, providers: Iterable[ProviderSpec]) -> ProviderSpec:
    """Read candidates once and require exactly one exact-name match."""
    raise NotImplementedError('Complete select_provider')

def load_provider(name: str, providers: Iterable[ProviderSpec]) -> TextProvider:
    """Load once; runtime checks establish callability, not a full signature."""
    raise NotImplementedError('Complete load_provider')

def bracket(text: str) -> str:
    return '[' + text + ']'

def main() -> None:
    try:
        candidates = [ProviderSpec('bracket', lambda: bracket)]
        provider = load_provider('bracket', candidates)
        print('loaded:', provider('ready'))
    except NotImplementedError as error:
        print('PDP4 starter unfinished:', error)
if __name__ == '__main__':
    main()
