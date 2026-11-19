"""Measure a flat module graph from syntax without executing its sources."""
import ast
import keyword
from collections.abc import Iterable, Mapping

def module_name(value: object) -> str:
    if not isinstance(value, str):
        raise TypeError('module names must be text')
    if not value.isidentifier() or keyword.iskeyword(value):
        raise ValueError('use flat Python module identifiers')
    return value

def dependency_map(sources: Mapping[str, str]) -> dict[str, tuple[str, ...]]:
    raise NotImplementedError('Complete dependency_map.')

def affected_modules(dependencies: Mapping[str, Iterable[str]], changed: str) -> tuple[str, ...]:
    raise NotImplementedError('Complete affected_modules.')

def main() -> None:
    sources = {'app': 'from model import Article\nfrom render import view', 'model': '', 'render': 'from model import Article'}
    graph = dependency_map(sources)
    print('imports:', graph)
    print('affected by model:', affected_modules(graph, 'model'))
if __name__ == '__main__':
    try:
        main()
    except NotImplementedError as error:
        print('starter unfinished:', error)
