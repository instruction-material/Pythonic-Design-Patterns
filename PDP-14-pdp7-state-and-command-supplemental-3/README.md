# Bounded Editor Undo

Store the previous immutable text on every replacement and retain only the newest limit entries. Undo is LIFO, returns False for an empty history, and restores the previous text exactly, including repeated and empty edits. Each document owns its own history. The oldest discarded state is outside the undo window.

Start in `starter/`; compare the complete reference in `solution/` after producing an independent attempt. Each imported role contains the runnable driver, contract tests and its brief.
