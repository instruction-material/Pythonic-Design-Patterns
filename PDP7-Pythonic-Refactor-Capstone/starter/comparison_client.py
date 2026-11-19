"""A separate client replaces an output provider without editing the workflow."""
from main import Article, Config, run_application


def compact(articles: tuple[Article, ...]) -> str:
    return "|".join(item.title for item in articles)


def main() -> None:
    rows = [{"title": " Hello World ", "kind": "blog", "body": " Python Patterns "}]
    saved: list[str] = []
    print("replacement:", run_application(Config(), lambda: rows, saved.append,
                                          {"text": compact}))
    print("saved:", saved)
    print("json:", run_application(Config(output="json"), lambda: rows,
                                   lambda document: None))


if __name__ == "__main__":
    main()
