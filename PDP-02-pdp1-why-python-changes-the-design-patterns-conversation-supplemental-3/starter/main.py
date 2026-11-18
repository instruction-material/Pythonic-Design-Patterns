"""PDP1 learner scaffold. Complete the named TODO bodies; the driver is supplied."""
from collections.abc import Callable, Iterable, Mapping
Formatter = Callable[[str], str]

def require_text(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError('text must be a string')
    return value

def make_rulebook(prefix: str) -> dict[str, Formatter]:
    """TODO: implement the contract in README.md."""
    raise NotImplementedError('Complete make_rulebook')

def select_formatter(name: str, rules: Mapping[str, Formatter]) -> Formatter:
    """TODO: implement the contract in README.md."""
    raise NotImplementedError('Complete select_formatter')

def format_named(messages: Iterable[str], name: str, rules: Mapping[str, Formatter]) -> list[str]:
    """Resolve once and preserve input order, including for custom rules."""
    formatter = select_formatter(name, rules)
    result = []
    for text in messages:
        result.append(require_text(formatter(require_text(text))))
    return result

def main() -> None:
    try:
        rules = make_rulebook('LOG: ')
        messages = ['design patterns', '']
        for name in rules:
            print(name + ':', format_named(messages, name, rules))
    except NotImplementedError as error:
        print('PDP1 starter unfinished:', error)
if __name__ == '__main__':
    main()
