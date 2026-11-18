"""Acquire a chosen resource set and release it in reverse order."""
from collections.abc import Iterator
from contextlib import ExitStack, contextmanager

def require_name(name: str) -> str:
    if not isinstance(name, str):
        raise TypeError('resource name must be a string')
    if not name.strip():
        raise ValueError('resource name must not be blank')
    return name

@contextmanager
def managed_resource(name: str, trace: list[str], *, fail_acquire: bool=False, suppress: bool=False) -> Iterator[str]:
    raise NotImplementedError('Complete managed_resource.')
    if False:
        yield name

def run_resources(names: list[str], trace: list[str], *, fail_at: str | None=None, fail_body: bool=False, suppress_at: str | None=None) -> str:
    raise NotImplementedError('Complete run_resources.')

def main() -> None:
    trace: list[str] = []
    try:
        result = run_resources(['profile', 'billing'], trace)
        print('result:', result)
        print('trace:', trace)
    except NotImplementedError:
        print('PDP6 starter unfinished: Complete managed_resource and run_resources.')
if __name__ == '__main__':
    main()
