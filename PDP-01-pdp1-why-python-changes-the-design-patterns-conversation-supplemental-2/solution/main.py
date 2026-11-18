"""Compare a function, a configured closure and a callable value."""

from collections.abc import Callable, Iterable
from dataclasses import dataclass

Formatter = Callable[[str], str]


def require_text(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError("text must be a string")
    return value


def title_case(text: str) -> str:
    """Use Python's title-casing rules; preserve surrounding whitespace."""
    return require_text(text).title()


def make_prefix_formatter(prefix: str) -> Formatter:
    """Capture one validated, immutable configuration value."""
    require_text(prefix)

    def format_text(text: str) -> str:
        return prefix + require_text(text)

    return format_text


@dataclass(frozen=True)
class PrefixFormatter:
    """Expose the same callable behavior with inspectable configuration."""

    prefix: str

    def __post_init__(self) -> None:
        require_text(self.prefix)

    def __call__(self, text: str) -> str:
        return self.prefix + require_text(text)


def format_messages(messages: Iterable[str], formatter: Formatter) -> list[str]:
    """Return new results in order without changing the input collection."""
    results = []
    for message in messages:
        result = formatter(require_text(message))
        results.append(require_text(result))
    return results


def main() -> None:
    messages = ["design patterns", ""]
    print("function:", format_messages(messages, title_case))
    print("closure:", format_messages(messages, make_prefix_formatter("LOG: ")))
    print("object:", format_messages(messages, PrefixFormatter("LOG: ")))


if __name__ == "__main__":
    main()
