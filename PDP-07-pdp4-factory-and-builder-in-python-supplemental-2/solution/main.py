"""Construct independent report values with a named function."""
from dataclasses import dataclass, replace


def require_text(text: str) -> str:
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if not text.strip():
        raise ValueError("text must contain a non-space character")
    return text


@dataclass(frozen=True)
class Config:
    title: str
    sections: tuple[str, ...] = ()
    footer: bool = False

    def __post_init__(self) -> None:
        require_text(self.title)
        if not isinstance(self.sections, tuple):
            raise TypeError("sections must be a tuple")
        for text in self.sections:
            require_text(text)
        if not isinstance(self.footer, bool):
            raise TypeError("footer must be a boolean")


def add_section(config: Config, section: str) -> Config:
    """Return a fresh value and preserve the original configuration."""
    if not isinstance(config, Config):
        raise TypeError("config must be a Config")
    require_text(section)
    return replace(config, sections=(*config.sections, section))


def render_text(config: Config) -> str:
    """Render the title, ordered sections and optional footer without mutation."""
    if not isinstance(config, Config):
        raise TypeError("config must be a Config")
    return "\n".join([config.title.upper(), *config.sections]
                     + (["-- end --"] if config.footer else []))


def main() -> None:
    try:
        base = Config("Plan")
        finished = add_section(add_section(base, "draft"), "reviewed")
        print("base sections:", len(base.sections))
        print(render_text(finished))
    except NotImplementedError as error:
        print("PDP4 starter unfinished:", error)


if __name__ == "__main__":
    main()
