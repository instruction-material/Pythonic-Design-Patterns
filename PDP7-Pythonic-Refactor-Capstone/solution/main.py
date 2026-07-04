from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol


#################
#   CONSTANTS   #
#################

ALL_KIND_FILTER = "all"
BLOG_KIND = "blog"
NEWS_KIND = "news"
BLOG_PREFIX = "[BLOG]"
NEWS_PREFIX = "[NEWS]"
OTHER_PREFIX = "[OTHER]"
RAW_TITLE_FIELD = "title"
RAW_KIND_FIELD = "kind"
RAW_BODY_FIELD = "body"
SAMPLE_ARTICLES = [
	{RAW_TITLE_FIELD: " Hello World ", RAW_KIND_FIELD: BLOG_KIND, RAW_BODY_FIELD: " Python Patterns "},
	{RAW_TITLE_FIELD: "System Update", RAW_KIND_FIELD: NEWS_KIND, RAW_BODY_FIELD: " adapters and facades "},
]


#############
#   TYPES   #
#############

# Store one normalized article
@dataclass(frozen=True)
class Article:
	"""Store article title, kind, and body"""

	title: str
	kind: str
	body: str


# Define the callable interface for normalizers
class Normalizer(Protocol):
	"""Define a function that normalizes one article"""

	def __call__(self, article: Article) -> Article:
		"""Normalize one article"""
		...


#################
#   FUNCTIONS   #
#################

def trim_and_lower(article: Article) -> Article:
	"""Trim whitespace and lowercase all article fields"""
	return Article(
		title=article.title.strip().lower(),
		kind=article.kind.strip().lower(),
		body=article.body.strip().lower(),
	)


def uppercase_normalizer(article: Article) -> Article:
	"""Uppercase the title and body of one article"""
	return Article(
		title=article.title.upper(),
		kind=article.kind,
		body=article.body.upper(),
	)


def compose_normalizers(*normalizers: Normalizer) -> Normalizer:
	"""Combine multiple normalizers into one normalizer"""
	# Run each normalizer in the order it was provided
	def run(article: Article) -> Article:
		"""Apply the composed normalizers to one article"""
		for normalizer in normalizers:
			article = normalizer(article)
		return article

	return run


def parse_article(raw_article: dict[str, str]) -> Article:
	"""Convert one raw article dictionary into an article"""
	return Article(
		title=raw_article[RAW_TITLE_FIELD],
		kind=raw_article[RAW_KIND_FIELD],
		body=raw_article[RAW_BODY_FIELD],
	)


def make_renderer() -> dict[str, Callable[[Article], str]]:
	"""Build renderers for each known article kind"""
	return {
		BLOG_KIND: lambda article: f"{BLOG_PREFIX} {article.title}: {article.body}",
		NEWS_KIND: lambda article: f"{NEWS_PREFIX} {article.title}: {article.body}",
	}


def render_other_article(article: Article) -> str:
	"""Render an article with an unknown kind"""
	return f"{OTHER_PREFIX} {article.title}: {article.body}"


def render_article(article: Article) -> str:
	"""Render one article using the matching renderer"""
	renderer = make_renderer().get(article.kind, render_other_article)
	return renderer(article)


def run_workflow(kind_filter: str, normalizer: Normalizer) -> str:
	"""Parse, filter, normalize, and render the sample articles"""
	results: list[str] = []

	# Process each raw article through the workflow
	for raw_article in SAMPLE_ARTICLES:
		article = parse_article(raw_article)

		# Skip articles that do not match the active kind filter
		if kind_filter != ALL_KIND_FILTER and article.kind != kind_filter:
			continue

		article = normalizer(article)
		results.append(render_article(article))

	return "\n".join(results)


def main() -> None:
	"""Run the capstone workflow with two normalization choices"""
	normalizer = compose_normalizers(trim_and_lower)
	print(run_workflow(ALL_KIND_FILTER, normalizer))
	print()
	print(
		run_workflow(
			BLOG_KIND,
			compose_normalizers(trim_and_lower, uppercase_normalizer),
		),
	)


if __name__ == "__main__":
	main()
