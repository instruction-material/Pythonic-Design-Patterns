"""Select a unique provider before invoking any third-party loader."""
from collections.abc import Callable, Iterable, Iterator
from contextlib import contextmanager
from importlib.metadata import entry_points
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from uuid import uuid4
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

PROVIDER_GROUP = "course.exporters.v1"


def discover_providers(group: str = PROVIDER_GROUP) -> list[ProviderSpec]:
    """Discover metadata first; EntryPoint.load stays lazy until selection."""
    return [ProviderSpec(point.name, point.load)
            for point in entry_points(group=group)]


@contextmanager
def metadata_fixture(
    entries: tuple[tuple[str, str], ...] = (("bracket", "bracket"),),
) -> Iterator[tuple[list[ProviderSpec], str]]:
    """Supply real local distribution metadata without a package installation."""
    token = uuid4().hex
    module_name = "_course_exporter_" + token
    group = PROVIDER_GROUP + ".fixture_" + token
    with TemporaryDirectory(prefix="course-provider-") as temporary:
        root = Path(temporary)
        (root / (module_name + ".py")).write_text(
            "def bracket(text: str) -> str:\n"
            "    return '[' + text + ']'\n", encoding="utf-8")
        for index, (name, target) in enumerate(entries):
            distribution = root / f"course_fixture_{token}_{index}-1.0.dist-info"
            distribution.mkdir()
            (distribution / "METADATA").write_text(
                "Metadata-Version: 2.1\n"
                f"Name: course-fixture-{token}-{index}\n"
                "Version: 1.0\n", encoding="utf-8")
            (distribution / "entry_points.txt").write_text(
                f"[{group}]\n{name} = {module_name}:{target}\n",
                encoding="utf-8")
        sys.path.insert(0, temporary)
        try:
            yield discover_providers(group), module_name
        finally:
            if temporary in sys.path:
                sys.path.remove(temporary)
            sys.modules.pop(module_name, None)


def bracket(text: str) -> str:
    return '[' + text + ']'

def main() -> None:
    try:
        with metadata_fixture() as (candidates, _):
            provider = load_provider('bracket', candidates)
            print('loaded:', provider('ready'))
    except NotImplementedError as error:
        print('PDP4 starter unfinished:', error)
if __name__ == '__main__':
    main()
