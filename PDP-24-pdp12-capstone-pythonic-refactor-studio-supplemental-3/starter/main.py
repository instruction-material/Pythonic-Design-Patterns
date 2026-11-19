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
        if not all((isinstance(value, str) for value in (self.title, self.kind, self.body))):
            raise TypeError('article fields must be text')
Renderer = Callable[[Article], str]

def make_registry(providers: Mapping[str, Renderer]) -> Mapping[str, Renderer]:
    raise NotImplementedError('Complete make_registry.')

def render_document(rows: Iterable[Article], providers: Mapping[str, Renderer], fallback: Renderer) -> str:
    raise NotImplementedError('Complete render_document.')

def plain(article: Article) -> str:
    return f'[BLOG] {article.title}: {article.body}'

def compact(article: Article) -> str:
    return f'{article.title} | {article.body}'

def other(article: Article) -> str:
    return f'[OTHER] {article.title}: {article.body}'

def main() -> None:
    rows = [Article('hello', 'blog', 'world')]
    print('baseline:', render_document(rows, make_registry({'blog': plain}), other))
    print('replaced:', render_document(rows, make_registry({'blog': compact}), other))
if __name__ == '__main__':
    try:
        main()
    except NotImplementedError as error:
        print('starter unfinished:', error)
