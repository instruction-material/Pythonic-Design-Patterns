# Captured Callable Queue

Capture the amount from the configuration when creating each callable. Execute the captured queue in order using a local integer accumulator. Later configuration or queue-list changes must not alter already captured values or membership. Validate the full queue before calling it; preserve the first callback exception. Callbacks may have external effects, which this local accumulator cannot reverse.

Start in `starter/`; compare the complete reference in `solution/` after producing an independent attempt. Each imported role contains the runnable driver, contract tests and its brief.
