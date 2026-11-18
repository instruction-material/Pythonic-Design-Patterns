"""Construct independent report values with a named function."""
from dataclasses import dataclass, replace

def require_text(text: str) -> str:
    if not isinstance(text, str):
        raise TypeError('text must be a string')
    if not text.strip():
        raise ValueError('text must contain a non-space character')
    return text

@dataclass(frozen=True)
class Config:
    title: str
    sections: tuple[str, ...] = ()
    footer: bool = False

    def __post_init__(self) -> None:
        require_text(self.title)
        if not isinstance(self.sections, tuple):
            raise TypeError('sections must be a tuple')
        for text in self.sections:
            require_text(text)
        if not isinstance(self.footer, bool):
            raise TypeError('footer must be a boolean')

def add_section(config: Config, section: str) -> Config:
    """Return a fresh value and preserve the original configuration."""
    raise NotImplementedError('Complete add_section')

def render_text(config: Config) -> str:
    """Render the title, ordered sections and optional footer without mutation."""
    raise NotImplementedError('Complete render_text')

def main() -> None:
    try:
        base = Config('Plan')
        finished = add_section(add_section(base, 'draft'), 'reviewed')
        print('base sections:', len(base.sections))
        print(render_text(finished))
    except NotImplementedError as error:
        print('PDP4 starter unfinished:', error)
if __name__ == '__main__':
    main()
