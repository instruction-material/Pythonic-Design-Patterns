"""Vendor failures and mutable payloads stop at one injected boundary."""
from collections.abc import Callable, Mapping


class SourceError(RuntimeError):
    pass


def fetch_values(fetch: Callable[[], Mapping[str, object]]) -> tuple[int, ...]:
    try:
        payload = fetch()
    except OSError as error:
        raise SourceError("vendor reader failed") from error
    if not isinstance(payload, Mapping):
        raise TypeError("vendor payload must be a mapping")
    values = payload.get("values", [])
    if not isinstance(values, list):
        raise TypeError("values must be a list")
    if any(not isinstance(v, int) or isinstance(v, bool) for v in values):
        raise TypeError("every value must be an integer")
    return tuple(values)


def highest_value(fetch: Callable[[], Mapping[str, object]]) -> int:
    values = fetch_values(fetch)
    if not values:
        raise ValueError("no values returned")
    return max(values)


def main() -> None:
    print("highest:", highest_value(lambda: {"values": [4, 9, 3]}))
    def failed_reader() -> Mapping[str, object]:
        raise TimeoutError("local simulated timeout")
    try:
        fetch_values(failed_reader)
    except SourceError as error:
        print("source failure:", type(error.__cause__).__name__)


if __name__ == "__main__":
    try:
        main()
    except NotImplementedError as error:
        print("starter unfinished:", error)
