"""Publish one validated event through a captured listener list."""
from collections.abc import Callable
from dataclasses import dataclass
from typing import cast
import inspect

@dataclass(frozen=True)
class Event:
    topic: str
    value: int

    def __post_init__(self) -> None:
        if not isinstance(self.topic, str):
            raise TypeError('topic must be a string')
        if not self.topic.strip():
            raise ValueError('topic must not be blank')
        if isinstance(self.value, bool) or not isinstance(self.value, int):
            raise TypeError('value must be an integer')
        if self.value < 0:
            raise ValueError('value must be nonnegative')
Listener = Callable[[Event], None]

def subscribe(listeners: list[Listener], callback: Listener) -> None:
    raise NotImplementedError('Complete subscribe.')

def publish_snapshot(listeners: list[Listener], event: Event) -> None:
    raise NotImplementedError('Complete publish_snapshot.')

def main() -> None:
    seen: list[str] = []
    listeners: list[Listener] = []

    def record(event: Event) -> None:
        seen.append(f'{event.topic}:{event.value}')

    def audit(event: Event) -> None:
        seen.append(f'audit:{event.value}')
    try:
        subscribe(listeners, record)
        subscribe(listeners, audit)
        publish_snapshot(listeners, Event('order', 3))
        print('delivery:', seen)
    except NotImplementedError:
        print('PDP5 starter unfinished: Complete subscribe and publish_snapshot.')
if __name__ == '__main__':
    main()
