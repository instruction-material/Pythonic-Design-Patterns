"""PDP1 learner scaffold. Complete the named TODO bodies; the driver is supplied."""
from collections.abc import Callable, Iterable
from dataclasses import dataclass
Formatter = Callable[[str], str]

def require_text(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError('text must be a string')
    return value

def title_case(text: str) -> str:
    """TODO: implement the contract in README.md."""
    raise NotImplementedError('Complete title_case')

def make_prefix_formatter(prefix: str) -> Formatter:
    """TODO: implement the contract in README.md."""
    raise NotImplementedError('Complete make_prefix_formatter')

@dataclass(frozen=True)
class PrefixFormatter:
    """Expose the same callable behavior with inspectable configuration."""
    prefix: str

    def __post_init__(self) -> None:
        require_text(self.prefix)

    def __call__(self, text: str) -> str:
        """TODO: implement the contract in README.md."""
        raise NotImplementedError('Complete __call__')

def format_messages(messages: Iterable[str], formatter: Formatter) -> list[str]:
    """Return new results in order without changing the input collection."""
    results = []
    for message in messages:
        result = formatter(require_text(message))
        results.append(require_text(result))
    return results

def main() -> None:
    try:
        messages = ['design patterns', '']
        print('function:', format_messages(messages, title_case))
        print('closure:', format_messages(messages, make_prefix_formatter('LOG: ')))
        print('object:', format_messages(messages, PrefixFormatter('LOG: ')))
    except NotImplementedError as error:
        print('PDP1 starter unfinished:', error)
if __name__ == '__main__':
    main()
