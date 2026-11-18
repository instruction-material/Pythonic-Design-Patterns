"""Select named callables through an explicit, caller-owned registry."""

from collections.abc import Callable, Iterable, Mapping

Formatter = Callable[[str], str]


def require_text(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError("text must be a string")
    return value


def make_rulebook(prefix: str) -> dict[str, Formatter]:
    """Return fresh rules; each closure retains its own prefix."""
    require_text(prefix)
    return {
        "title": lambda text: require_text(text).title(),
        "prefix": lambda text: prefix + require_text(text),
        "identity": require_text,
    }


def select_formatter(name: str, rules: Mapping[str, Formatter]) -> Formatter:
    """Reject missing choices and non-callables without mutating rules."""
    require_text(name)
    try:
        formatter = rules[name]
    except KeyError as error:
        raise ValueError(f"Unknown formatter: {name}") from error
    if not callable(formatter):
        raise TypeError("a formatter must be callable")
    return formatter


def format_named(
    messages: Iterable[str], name: str, rules: Mapping[str, Formatter]
) -> list[str]:
    """Resolve once and preserve input order, including for custom rules."""
    formatter = select_formatter(name, rules)
    result = []
    for text in messages:
        result.append(require_text(formatter(require_text(text))))
    return result


def main() -> None:
    rules = make_rulebook("LOG: ")
    messages = ["design patterns", ""]
    for name in rules:
        print(name + ":", format_named(messages, name, rules))


if __name__ == "__main__":
    main()
