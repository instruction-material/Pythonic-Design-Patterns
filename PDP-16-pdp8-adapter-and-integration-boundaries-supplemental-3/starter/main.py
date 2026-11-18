"""Vendor failures and mutable payloads stop at one injected boundary."""
from collections.abc import Callable, Mapping

class SourceError(RuntimeError):
    pass

def fetch_values(fetch: Callable[[], Mapping[str, object]]) -> tuple[int, ...]:
    raise NotImplementedError('Complete fetch_values')

def highest_value(fetch: Callable[[], Mapping[str, object]]) -> int:
    raise NotImplementedError('Complete highest_value')

def main() -> None:
    print('highest:', highest_value(lambda: {'values': [4, 9, 3]}))

    def failed_reader() -> Mapping[str, object]:
        raise TimeoutError('local simulated timeout')
    try:
        fetch_values(failed_reader)
    except SourceError as error:
        print('source failure:', type(error.__cause__).__name__)
if __name__ == '__main__':
    try:
        main()
    except NotImplementedError as error:
        print('starter unfinished:', error)
