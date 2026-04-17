ARTICLES = [
	{"title": " Hello World ", "kind": "blog", "body": " Python Patterns "},
	{"title": "System Update", "kind": "news", "body": " adapters and facades "},
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


if __name__ == "__main__":
	main()
