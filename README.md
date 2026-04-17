# Pythonic Design Patterns

This folder is structured as the future
`instruction-material/Pythonic-Design-Patterns` repository for the site course.

The materials follow the core project sequence used by the course:

1. `PDP1-Strategy-Rulebook`
2. `PDP2-Factory-and-Builder-Config-Kit`
3. `PDP3-Observer-Notification-Hub`
4. `PDP4-Decorator-Proxy-Facade-Toolkit`
5. `PDP5-State-Command-Quest-Loop`
6. `PDP6-Adapter-Template-Import-Pipeline`
7. `PDP7-Pythonic-Refactor-Capstone`

Each project contains:

- `starter/` with a guided scaffold and TODO-style simplifications
- `solution/` with a complete reference implementation
- `README.md` describing the engineering goal and how it fits the course

## Tooling

Preferred IDEs:

- `PyCharm`
- `VS Code`

Expected local toolchain:

- `python3`
- `venv`
- optional `pytest` for extra refactoring safety

## Local Validation Workflow

From this folder:

1. `python3 -m compileall .`
2. Run any selected starter or solution with `python3 path/to/main.py`

## Teaching Notes

- Ask students to justify why a plain function, module, or data class was not enough before they add a pattern-shaped layer.
- Pair every pattern lesson with one explicit "keep it simpler" decision.
- Keep the course grounded in maintainability, boundary cleanup, and refactoring rather than pattern collecting.
