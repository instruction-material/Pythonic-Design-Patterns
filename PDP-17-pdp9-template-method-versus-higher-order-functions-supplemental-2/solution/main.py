"""Compare a fixed workflow's hooks with explicitly composed callables."""
from collections.abc import Callable, Iterable

IntStep = Callable[[int], int]


def integer(value: object) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError("values and stage results must be integers")
    return value


def compose_stages(*steps: IntStep) -> IntStep:
    if not all(callable(step) for step in steps):
        raise TypeError("each stage must be callable")
    owned = tuple(steps)

    def composed(value: int) -> int:
        result = integer(value)
        for step in owned:
            result = integer(step(result))
        return result

    return composed


def run_steps(values: Iterable[int], step: IntStep) -> list[int]:
    if not callable(step):
        raise TypeError("step must be callable")
    owned = tuple(integer(value) for value in values)
    return [integer(step(value)) for value in owned]


class TemplatePipeline:
    def transform(self, value: int) -> int:
        return value

    def run(self, values: Iterable[int]) -> list[int]:
        return run_steps(values, self.transform)


class AddThenDouble(TemplatePipeline):
    def transform(self, value: int) -> int:
        return (value + 1) * 2


def main() -> None:
    values = [1, 2]
    print("functional:", run_steps(values, compose_stages(lambda n: n + 1, lambda n: n * 2)))
    print("template:", AddThenDouble().run(values))
    print("input:", values)


if __name__ == "__main__":
    try:
        main()
    except NotImplementedError as error:
        print("starter unfinished:", error)
