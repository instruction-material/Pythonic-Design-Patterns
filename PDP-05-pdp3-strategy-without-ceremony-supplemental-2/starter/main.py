"""Apply one score rule and construct a repeatable configured callable."""
from collections.abc import Callable
ScoreRule = Callable[[int], int]

def require_score(value: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError('score must be an integer')
    if value < 0:
        raise ValueError('score must be nonnegative')
    return value

def run_rule(score: int, rule: ScoreRule) -> int:
    """Call the rule once and validate its resulting score."""
    raise NotImplementedError('Complete run_rule')

def make_bonus_rule(bonus: int) -> ScoreRule:
    """Capture one valid bonus without accumulating per-call state."""
    raise NotImplementedError('Complete make_bonus_rule')

def main() -> None:
    try:
        bonus = make_bonus_rule(3)
        print('doubled:', run_rule(4, lambda value: value * 2))
        print('bonus:', run_rule(4, bonus))
        print('repeat:', run_rule(4, bonus))
    except NotImplementedError as error:
        print('PDP3 starter unfinished:', error)
if __name__ == '__main__':
    main()
