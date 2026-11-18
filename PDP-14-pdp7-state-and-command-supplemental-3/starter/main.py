"""A bounded history defines exactly which local edits can still be reversed."""

class Document:

    def __init__(self, text: str='', *, limit: int=2) -> None:
        if not isinstance(text, str):
            raise TypeError('text must be a string')
        if not isinstance(limit, int) or isinstance(limit, bool):
            raise TypeError('limit must be an integer')
        if limit < 1:
            raise ValueError('limit must be positive')
        self._text, self._limit = (text, limit)
        self._undo: list[str] = []

    @property
    def text(self) -> str:
        return self._text

    @property
    def history(self) -> tuple[str, ...]:
        return tuple(self._undo)

def apply_edit(document: Document, text: str) -> None:
    raise NotImplementedError('Complete apply_edit')

def undo_edit(document: Document) -> bool:
    raise NotImplementedError('Complete undo_edit')

def main() -> None:
    document = Document()
    for text in ['first', 'second', 'third']:
        apply_edit(document, text)
    print('edited:', document.text)
    undo_edit(document)
    print('undo:', document.text)
    undo_edit(document)
    print('undo:', document.text)
    print('empty:', undo_edit(document))
if __name__ == '__main__':
    try:
        main()
    except NotImplementedError as error:
        print('starter unfinished:', error)
