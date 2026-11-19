"""An explicit surrounding context owns a lazy stream's lifetime."""
from collections.abc import Generator, Iterable, Iterator
from contextlib import contextmanager
from io import StringIO


def integer(value: object) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError("values must be integers")
    return value


@contextmanager
def managed_values(values: Iterable[int], events: list[str]) -> Iterator[Generator[int, None, None]]:
    owned = tuple(integer(value) for value in values)
    resource = StringIO("".join(str(value) + "\n" for value in owned))
    events.append("open")
    stream = (int(line) for line in resource)
    try:
        yield stream
    finally:
        stream.close()
        resource.close()
        events.append("close")


def take_values(values: Iterator[int], count: int) -> list[int]:
    integer(count)
    if count < 0:
        raise ValueError("count must be nonnegative")
    result: list[int] = []
    for _ in range(count):
        try:
            result.append(next(values))
        except StopIteration:
            break
    return result


def main() -> None:
    events: list[str] = []
    with managed_values([3, 5, 8], events) as values:
        print("partial:", take_values(values, 2))
    print("after:", next(values, "closed"))
    print("events:", events)


if __name__ == "__main__":
    try:
        main()
    except NotImplementedError as error:
        print("starter unfinished:", error)
