"""Pure preparation preserves the legacy filter and field-access order."""
from models import Article, Rows


def prepare(rows: Rows, kind_filter: str, uppercase: bool) -> tuple[Article, ...]:
    prepared: list[Article] = []
    for row in rows:
        if kind_filter != "all" and row["kind"] != kind_filter:
            continue
        title = row["title"].strip().lower()
        body = row["body"].strip().lower()
        if uppercase:
            title = title.upper()
            body = body.upper()
        prepared.append(Article(title, row["kind"], body))
    return tuple(prepared)
