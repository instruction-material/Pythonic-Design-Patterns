"""Separate deterministic preparation from externally visible writes."""
from collections.abc import Callable, Iterable

def normalize_rows(rows: Iterable[str]) -> tuple[str, ...]:
    raise NotImplementedError('Complete normalize_rows.')

def publish_rows(rows: Iterable[str], write: Callable[[str], None]) -> int:
    raise NotImplementedError('Complete publish_rows.')

def main() -> None:
    written: list[str] = []
    count = publish_rows([' alpha ', '', ' beta '], written.append)
    print('written:', written)
    print('count:', count)
if __name__ == '__main__':
    try:
        main()
    except NotImplementedError as error:
        print('starter unfinished:', error)
