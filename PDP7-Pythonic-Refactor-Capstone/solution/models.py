"""Immutable application values and explicit collaborator types."""
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    kind_filter: str = "all"
    uppercase: bool = False
    output: str = "text"

    def __post_init__(self) -> None:
        if not isinstance(self.kind_filter, str) or not isinstance(self.output, str):
            raise TypeError("filter and output must be text")
        if not self.output or self.output != self.output.strip():
            raise ValueError("output must be nonempty and trimmed")
        if not isinstance(self.uppercase, bool):
            raise TypeError("uppercase must be bool")


@dataclass(frozen=True)
class Article:
    title: str
    kind: str
    body: str


Rows = Iterable[Mapping[str, str]]
Reader = Callable[[], Rows]
Writer = Callable[[str], None]
Renderer = Callable[[tuple[Article, ...]], str]
