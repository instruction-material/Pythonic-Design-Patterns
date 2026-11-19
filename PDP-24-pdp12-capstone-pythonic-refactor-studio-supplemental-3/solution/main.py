"""Replace one renderer through an owned explicit registry."""
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from types import MappingProxyType


@dataclass(frozen=True)
class Article:
    title: str
    kind: str
    body: str

    def __post_init__(self) -> None:
        if not all(isinstance(value, str) for value in (self.title, self.kind, self.body)):
            raise TypeError("article fields must be text")


Renderer = Callable[[Article], str]


def make_registry(providers: Mapping[str, Renderer]) -> Mapping[str, Renderer]:
    owned = dict(providers)
    for name, provider in owned.items():
        if not isinstance(name, str):
            raise TypeError("provider names must be text")
        if not name or name != name.strip():
            raise ValueError("provider names must be nonempty and trimmed")
        if not callable(provider):
            raise TypeError("providers must be callable")
    return MappingProxyType(owned)


def render_document(rows: Iterable[Article], providers: Mapping[str, Renderer],
                    fallback: Renderer) -> str:
    registry = make_registry(providers)
    if not callable(fallback):
        raise TypeError("fallback must be callable")
    owned = tuple(rows)
    if not all(isinstance(row, Article) for row in owned):
        raise TypeError("rows must contain Article values")
    rendered: list[str] = []
    for row in owned:
        result = registry.get(row.kind, fallback)(row)
        if not isinstance(result, str):
            raise TypeError("renderers must return text")
        rendered.append(result)
    return "\n".join(rendered)


def plain(article: Article) -> str:
    return f"[BLOG] {article.title}: {article.body}"


def compact(article: Article) -> str:
    return f"{article.title} | {article.body}"


def other(article: Article) -> str:
    return f"[OTHER] {article.title}: {article.body}"


def main() -> None:
    rows = [Article("hello", "blog", "world")]
    print("baseline:", render_document(rows, make_registry({"blog": plain}), other))
    print("replaced:", render_document(rows, make_registry({"blog": compact}), other))


if __name__ == "__main__":
    try:
        main()
    except NotImplementedError as error:
        print("starter unfinished:", error)
