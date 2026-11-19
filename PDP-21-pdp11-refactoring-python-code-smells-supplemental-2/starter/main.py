"""Characterize a small transformation before replacing its structure."""
from collections.abc import Callable, Iterable, Mapping

def format_legacy(rows: Iterable[Mapping[str, str]], kind_filter: str='all', uppercase: bool=False) -> str:
    results: list[str] = []
    for row in rows:
        if kind_filter != 'all' and row['kind'] != kind_filter:
            continue
        title = row['title'].strip().lower()
        body = row['body'].strip().lower()
        if uppercase:
            title, body = (title.upper(), body.upper())
        if row['kind'] == 'blog':
            results.append(f'[BLOG] {title}: {body}')
        elif row['kind'] == 'news':
            results.append(f'[NEWS] {title}: {body}')
        else:
            results.append(f'[OTHER] {title}: {body}')
    return '\n'.join(results)

def render_fields(title: str, body: str, kind: str) -> str:
    prefix = {'blog': 'BLOG', 'news': 'NEWS'}.get(kind, 'OTHER')
    return f'[{prefix}] {title}: {body}'

def format_refactored(rows: Iterable[Mapping[str, str]], kind_filter: str='all', uppercase: bool=False) -> str:
    raise NotImplementedError('Complete format_refactored.')

def capture_outcome(operation: Callable[[], str]) -> tuple[str, str]:
    raise NotImplementedError('Complete capture_outcome.')

def main() -> None:
    rows = [{'title': ' Hello ', 'kind': ' BLOG ', 'body': ' World '}]
    before = capture_outcome(lambda: format_legacy(rows))
    after = capture_outcome(lambda: format_refactored(rows))
    print('baseline:', before)
    print('same:', before == after)
if __name__ == '__main__':
    try:
        main()
    except NotImplementedError as error:
        print('starter unfinished:', error)
