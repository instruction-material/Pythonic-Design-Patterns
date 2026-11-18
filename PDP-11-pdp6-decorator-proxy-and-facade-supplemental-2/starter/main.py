"""Trace a synchronous calculation with preserved public metadata."""
from collections.abc import Callable, Iterable
from functools import wraps
import inspect
from typing import ParamSpec, TypeVar
P = ParamSpec('P')
R = TypeVar('R')

def require_label(label: str) -> str:
    if not isinstance(label, str):
        raise TypeError('label must be a string')
    if not label.strip():
        raise ValueError('label must not be blank')
    return label

def make_traced(label: str, trace: list[str], func: Callable[P, R]) -> Callable[P, R]:
    raise NotImplementedError('Complete make_traced.')

def compose_layers(func: Callable[P, R], labels: Iterable[str], trace: list[str]) -> Callable[P, R]:
    raise NotImplementedError('Complete compose_layers.')

def calculate(value: int, *, offset: int=1) -> int:
    """Return a doubled value with a named offset."""
    return value * 2 + offset

def main() -> None:
    trace: list[str] = []
    try:
        operation = compose_layers(calculate, ['audit', 'metrics'], trace)
        print('result:', operation(4, offset=1))
        print('trace:', trace)
    except NotImplementedError:
        print('PDP6 starter unfinished: Complete make_traced and compose_layers.')
if __name__ == '__main__':
    main()
