"""Working mixed workflow. Characterize it before extracting responsibilities."""
from collections.abc import Mapping
import json
from types import MappingProxyType
from models import Article as Article, Config as Config, Reader, Renderer, Writer

ARTICLES = [
    {"title": " Hello World ", "kind": "blog", "body": " Python Patterns "},
    {
        "title": "System Update",
        "kind": "news",
        "body": " adapters and facades ",
    },
]


def run_workflow(kind_filter: str, uppercase: bool) -> str:
    results = []
    for article in ARTICLES:
        if kind_filter != "all" and article["kind"] != kind_filter:
            continue

        title = article["title"].strip().lower()
        body = article["body"].strip().lower()

        if uppercase:
            title = title.upper()
            body = body.upper()

        if article["kind"] == "blog":
            results.append(f"[BLOG] {title}: {body}")
        elif article["kind"] == "news":
            results.append(f"[NEWS] {title}: {body}")
        else:
            results.append(f"[OTHER] {title}: {body}")

    return "\n".join(results)


def main() -> None:
    print(run_workflow("all", uppercase=False))




def run_application(config: Config, reader: Reader, writer: Writer,
                    providers: Mapping[str, Renderer] | None = None) -> str:
    if not isinstance(config, Config):
        raise TypeError("config must be Config")
    if not callable(reader) or not callable(writer):
        raise TypeError("reader and writer must be callable")

    def text_output(articles: tuple[Article, ...]) -> str:
        lines: list[str] = []
        for item in articles:
            if item.kind == "blog":
                label = "BLOG"
            elif item.kind == "news":
                label = "NEWS"
            else:
                label = "OTHER"
            lines.append(f"[{label}] {item.title}: {item.body}")
        return "\n".join(lines)

    def json_output(articles: tuple[Article, ...]) -> str:
        return json.dumps([
            {"title": item.title, "kind": item.kind, "body": item.body}
            for item in articles
        ], ensure_ascii=False, separators=(",", ":"))

    registry: dict[str, Renderer] = {"text": text_output, "json": json_output}
    if providers is not None:
        registry.update(providers)
    for name, provider in registry.items():
        if not isinstance(name, str):
            raise TypeError("provider names must be text")
        if not name or name != name.strip():
            raise ValueError("provider names must be nonempty and trimmed")
        if not callable(provider):
            raise TypeError("providers must be callable")
    renderer = MappingProxyType(registry)[config.output]
    owned = tuple(dict(row) for row in reader())
    articles: list[Article] = []
    for row in owned:
        if config.kind_filter != "all" and row["kind"] != config.kind_filter:
            continue
        title = row["title"].strip().lower()
        body = row["body"].strip().lower()
        if config.uppercase:
            title = title.upper()
            body = body.upper()
        articles.append(Article(title, row["kind"], body))
    document = renderer(tuple(articles))
    if not isinstance(document, str):
        raise TypeError("renderer must return text")
    writer(document)
    return document


if __name__ == "__main__":
    main()
