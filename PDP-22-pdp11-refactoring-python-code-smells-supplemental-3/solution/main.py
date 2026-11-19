"""Separate deterministic preparation from externally visible writes."""
from collections.abc import Callable, Iterable


def normalize_rows(rows: Iterable[str]) -> tuple[str, ...]:
    owned = tuple(rows)
    if not all(isinstance(row, str) for row in owned):
        raise TypeError("rows must contain text")
    return tuple(cleaned for row in owned if (cleaned := row.strip()))


def publish_rows(rows: Iterable[str], write: Callable[[str], None]) -> int:
    if not callable(write):
        raise TypeError("writer must be callable")
    prepared = normalize_rows(rows)
    for row in prepared:
        write(row)
    return len(prepared)


def main() -> None:
    written: list[str] = []
    count = publish_rows([" alpha ", "", " beta "], written.append)
    print("written:", written)
    print("count:", count)


if __name__ == "__main__":
    try:
        main()
    except NotImplementedError as error:
        print("starter unfinished:", error)
