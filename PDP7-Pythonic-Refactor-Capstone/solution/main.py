from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol


RAW_ARTICLES = [
	{"title": " Hello World ", "kind": "blog", "body": " Python Patterns "},
	{"title": "System Update", "kind": "news", "body": " adapters and facades "},
]


@dataclass(frozen=True)
class Article:
	title: str
	kind: str
	body: str


class Normalizer(Protocol):
	def __call__(self, article: Article) -> Article: ...


def trim_and_lower(article: Article) -> Article:
	return Article(
		title=article.title.strip().lower(),
		kind=article.kind.strip().lower(),
		body=article.body.strip().lower(),
	)


def uppercase_normalizer(article: Article) -> Article:
	return Article(
		title=article.title.upper(),
		kind=article.kind,
		body=article.body.upper(),
	)


def compose_normalizers(*normalizers: Normalizer) -> Normalizer:
	def run(article: Article) -> Article:
		for normalizer in normalizers:
			article = normalizer(article)
		return article

	return run


def parse_article(raw: dict[str, str]) -> Article:
	return Article(title=raw["title"], kind=raw["kind"], body=raw["body"])


def make_renderer() -> dict[str, Callable[[Article], str]]:
	return {
		"blog": lambda article: f"[BLOG] {article.title}: {article.body}",
		"news": lambda article: f"[NEWS] {article.title}: {article.body}",
	}


def render_article(article: Article) -> str:
	renderer = make_renderer().get(
		article.kind,
		lambda current: f"[OTHER] {current.title}: {current.body}",
	)
	return renderer(article)


def run_workflow(kind_filter: str, normalizer: Normalizer) -> str:
	results: list[str] = []
	for raw_article in RAW_ARTICLES:
		article = parse_article(raw_article)
		if kind_filter != "all" and article.kind != kind_filter:
			continue
		article = normalizer(article)
		results.append(render_article(article))
	return "\n".join(results)


def main() -> None:
	normalizer = compose_normalizers(trim_and_lower)
	print(run_workflow("all", normalizer))
	print()
	print(run_workflow("blog", compose_normalizers(trim_and_lower, uppercase_normalizer)))


if __name__ == "__main__":
	main()
