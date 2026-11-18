"""A callable command captures configuration instead of consulting it later."""
from collections.abc import Callable, Iterable, Mapping

def integer(value: object) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError('queue values must be integers')
    return value

def make_increment(config: Mapping[str, int]) -> Callable[[int], int]:
    raise NotImplementedError('Complete make_increment')

def run_queue(initial: int, actions: Iterable[Callable[[int], int]]) -> int:
    raise NotImplementedError('Complete run_queue')

def main() -> None:
    config = {'amount': 3}
    increment = make_increment(config)
    config['amount'] = 100
    print('result:', run_queue(3, [increment, increment]))
    print('config now:', config['amount'])
if __name__ == '__main__':
    try:
        main()
    except NotImplementedError as error:
        print('starter unfinished:', error)
