"""An explicit surrounding context owns a lazy stream's lifetime."""
from collections.abc import Generator, Iterable, Iterator
from contextlib import contextmanager
from io import StringIO

def integer(value: object) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError('values must be integers')
    return value

@contextmanager
def managed_values(values: Iterable[int], events: list[str]) -> Iterator[Generator[int, None, None]]:
    raise NotImplementedError('Complete managed_values.')

def take_values(values: Iterator[int], count: int) -> list[int]:
    raise NotImplementedError('Complete take_values.')

def main() -> None:
    events: list[str] = []
    with managed_values([3, 5, 8], events) as values:
        print('partial:', take_values(values, 2))
    print('after:', next(values, 'closed'))
    print('events:', events)
if __name__ == '__main__':
    try:
        main()
    except NotImplementedError as error:
        print('starter unfinished:', error)
