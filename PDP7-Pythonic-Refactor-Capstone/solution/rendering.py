"""Output providers own formatting, with no I/O or global registry."""
from collections.abc import Mapping
import json
from types import MappingProxyType
from models import Article, Renderer


def render_text(articles: tuple[Article, ...]) -> str:
    lines: list[str] = []
    for article in articles:
        if article.kind == "blog":
            label = "BLOG"
        elif article.kind == "news":
            label = "NEWS"
        else:
            label = "OTHER"
        lines.append(f"[{label}] {article.title}: {article.body}")
    return "\n".join(lines)


def render_json(articles: tuple[Article, ...]) -> str:
    return json.dumps([
        {"title": item.title, "kind": item.kind, "body": item.body}
        for item in articles
    ], ensure_ascii=False, separators=(",", ":"))


def make_registry(providers: Mapping[str, Renderer] | None = None
                  ) -> Mapping[str, Renderer]:
    owned: dict[str, Renderer] = {"text": render_text, "json": render_json}
    if providers is not None:
        owned.update(providers)
    for name, provider in owned.items():
        if not isinstance(name, str):
            raise TypeError("provider names must be text")
        if not name or name != name.strip():
            raise ValueError("provider names must be nonempty and trimmed")
        if not callable(provider):
            raise TypeError("providers must be callable")
    return MappingProxyType(owned)
