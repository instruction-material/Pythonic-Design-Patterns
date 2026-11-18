"""Compare named score strategies once each, retaining insertion-order ties."""
from collections.abc import Callable, Mapping
ScoreRule = Callable[[int], int]

def require_score(value: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError('score must be an integer')
    if value < 0:
        raise ValueError('score must be nonnegative')
    return value

def require_name(name: str) -> str:
    if not isinstance(name, str):
        raise TypeError('name must be a string')
    if not name.strip():
        raise ValueError('name must contain a non-space character')
    return name

def register_score_rule(rules: dict[str, ScoreRule], name: str, rule: ScoreRule) -> None:
    """Validate first; reject a duplicate without modifying the registry."""
    raise NotImplementedError('Complete register_score_rule')

def choose_best(score: int, rules: Mapping[str, ScoreRule]) -> tuple[str, int]:
    """Use a binding snapshot; equal results keep the earlier binding."""
    raise NotImplementedError('Complete choose_best')

def main() -> None:
    try:
        rules: dict[str, ScoreRule] = {}
        register_score_rule(rules, 'double', lambda value: value * 2)
        register_score_rule(rules, 'bonus', lambda value: value + 5)
        name, score = choose_best(4, rules)
        print('winner:', name, score)
        print('rules:', list(rules))
    except NotImplementedError as error:
        print('PDP3 starter unfinished:', error)
if __name__ == '__main__':
    main()
