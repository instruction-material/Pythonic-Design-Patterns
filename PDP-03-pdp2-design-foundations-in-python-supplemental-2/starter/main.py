"""Compose a validated value, a pure renderer and a replaceable sender."""
from dataclasses import dataclass, field
from typing import Protocol

def require_text(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError('text must be a string')
    return value

@dataclass(frozen=True)
class Notice:
    topic: str
    text: str

    def __post_init__(self) -> None:
        if not require_text(self.topic).strip():
            raise ValueError('topic must contain a non-space character')
        require_text(self.text)

class Sender(Protocol):

    def send(self, text: str, /) -> None:
        """Send one formatted string."""
        ...

@dataclass
class MemorySender:
    messages: list[str] = field(default_factory=list)

    def send(self, text: str) -> None:
        self.messages.append(require_text(text))

def require_notice(notice: Notice) -> Notice:
    if not isinstance(notice, Notice):
        raise TypeError('notice must be a Notice')
    return notice

def require_sender(sender: Sender) -> None:
    if not callable(getattr(sender, 'send', None)):
        raise TypeError('sender must provide a callable send')

def render_notice(notice: Notice) -> str:
    raise NotImplementedError('Complete render_notice')

def deliver_notice(notice: Notice, sender: Sender) -> str:
    raise NotImplementedError('Complete deliver_notice')

def main() -> None:
    try:
        first, second = (MemorySender(), MemorySender())
        notice = Notice('build', 'ready')
        print('rendered:', deliver_notice(notice, first))
        deliver_notice(Notice('build', ''), first)
        deliver_notice(notice, second)
        print('first:', first.messages)
        print('second:', second.messages)
    except NotImplementedError as error:
        print('PDP2 starter unfinished:', error)
if __name__ == '__main__':
    main()
