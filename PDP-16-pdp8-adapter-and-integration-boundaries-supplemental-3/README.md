# Injected Vendor Boundary

Call an injected zero-argument reader exactly once. Translate {values:[integers]} into an owned immutable tuple; missing values defaults to an empty list, extra fields are ignored, bool/float values are rejected. Wrap reader OSError/TimeoutError as SourceError with the original cause. Preserve programming exceptions. Compute a maximum for nonempty data and raise ValueError for empty data. Use local readers without network access.

Start in `starter/`; compare the complete reference in `solution/` after producing an independent attempt. Each imported role contains the runnable driver, contract tests and its brief.
