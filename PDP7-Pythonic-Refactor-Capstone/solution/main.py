"""Composition root and compatibility entry point."""
from collections.abc import Mapping
from models import Article as Article, Config as Config, Reader, Renderer, Writer
from processing import prepare
from rendering import make_registry, render_text

ARTICLES = [
    {"title": " Hello World ", "kind": "blog", "body": " Python Patterns "},
    {"title": "System Update", "kind": "news", "body": " adapters and facades "},
]


def run_workflow(kind_filter: str, uppercase: bool) -> str:
    return render_text(prepare(ARTICLES, kind_filter, uppercase))


def run_application(config: Config, reader: Reader, writer: Writer,
                    providers: Mapping[str, Renderer] | None = None) -> str:
    if not isinstance(config, Config):
        raise TypeError("config must be Config")
    if not callable(reader) or not callable(writer):
        raise TypeError("reader and writer must be callable")
    registry = make_registry(providers)
    renderer = registry[config.output]
    owned = tuple(dict(row) for row in reader())
    articles = prepare(owned, config.kind_filter, config.uppercase)
    document = renderer(articles)
    if not isinstance(document, str):
        raise TypeError("renderer must return text")
    writer(document)
    return document


def main() -> None:
    print(run_workflow("all", uppercase=False))


if __name__ == "__main__":
    main()
