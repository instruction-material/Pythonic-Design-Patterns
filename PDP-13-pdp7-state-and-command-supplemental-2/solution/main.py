"""A callable command captures configuration instead of consulting it later."""
from collections.abc import Callable, Iterable, Mapping


def integer(value: object) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError("queue values must be integers")
    return value


def make_increment(config: Mapping[str, int]) -> Callable[[int], int]:
    amount = integer(config["amount"])
    def increment(value: int) -> int:
        return integer(value) + amount
    return increment


def run_queue(initial: int, actions: Iterable[Callable[[int], int]]) -> int:
    value = integer(initial)
    captured = tuple(actions)
    if any(not callable(action) for action in captured):
        raise TypeError("every queue entry must be callable")
    for action in captured:
        value = integer(action(value))
    return value


def main() -> None:
    config = {"amount": 3}
    increment = make_increment(config)
    config["amount"] = 100
    print("result:", run_queue(3, [increment, increment]))
    print("config now:", config["amount"])


if __name__ == "__main__":
    try:
        main()
    except NotImplementedError as error:
        print("starter unfinished:", error)
