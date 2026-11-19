# Pythonic Refactor Studio

This complete reference separates pure preparation, output providers and composition while preserving the learner baseline. Use its decisions as one justified design, not a required class hierarchy.

## Protected behavior

`run_workflow(kind_filter, uppercase)` retains the complete original program's signature, two-line default output, filtering before field access, raw kind matching, order, duplicates, case conversion and exception details. The unchanged `baseline_original.py` is the oracle, SHA-256 `bac4d05d399d0b801aef75ecf93bae46e67c1f3d992366a2458b8220c879435b` using LF text. Padded ` BLOG ` remains OTHER. A filtered record missing kind raises `KeyError("kind")`; with filter all, missing title is encountered first. Changing these rules is an intentional feature or bug fix with separate evidence.

## Application contract

`run_application(config, reader, writer, providers=None)` is a separate explicit application boundary. Frozen `Config` supplies filter, uppercase and output name. A provider is a callable taking a tuple of frozen `Article` values and returning text. Built-in text and deterministic compact JSON providers can be replaced by an explicitly supplied registry entry. Validate setup and copy the registry before any I/O; reject an unknown output name before reading. Read once, copy each record into an owned tuple, prepare the complete document, then write once, including an empty document. Return the exact written text. Source, preparation and renderer failures cause no write and preserve the exception; writer failure preserves its exception and any external effect already made. This is an in-memory snapshot, not a database transaction. Reader/writer resource acquisition and closing belong to their caller. Config validation is an intentional contract of this new API, separate from the original entry point.

The old unqualified reference normalized kind and accepted a normalizer as its second argument. This pack preserves the learner's original boolean API. A future normalization feature requires a separate entry point or a deliberate API migration and changed-behavior tests.

## Verify and retain evidence

Use Python 3.14. Runtime dependencies are standard library only; development pins are unchanged. In an exported folder:

```sh
python3.14 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -B main.py
.venv/bin/python -B comparison_client.py
.venv/bin/python -B -m unittest discover -s . -p test_contract.py -v
.venv/bin/python -m mypy --strict --no-incremental --python-version 3.14 main.py models.py baseline_original.py comparison_client.py
```

For the split reference, include `processing.py rendering.py` in the final checker command. Windows uses `py -3.14 -m venv .venv` and `.venv\Scripts\python.exe`. Run the original tests unchanged. The first group compares 72 combinations against the frozen original; fourteen further groups cover the application boundary. Retain exact interpreter/checker versions, full test/type output, default output, before/after dependency maps, a small change diff, design decisions, a rollback commit or complete export, and evidence from two change scenarios.

Default output:

```text
[BLOG] hello world: python patterns
[NEWS] system update: adapters and facades
```

Replacement client output:

```text
replacement: hello world
saved: ['hello world']
json: [{"title":"hello world","kind":"blog","body":"python patterns"}]
```

## Distinct course tasks

For PDP11, characterize the working program, then extract one pure preparation or formatting responsibility in a small reversible change. Preserve both public APIs and the oracle matrix. The optional capstone client adds a Unicode/malformed-record characterization table and records whether each discovered behavior is preserved or deliberately changed.

For PDP12, complete the multi-module refactor, place composition at the application edge, produce dependency maps and a decision record, and demonstrate two independent changes: replace the text provider and switch to the JSON provider through a separate client. Explain which modules changed and why. The optional project adds a new explicitly injected reader and records source failure, output failure and ownership at that boundary. It must preserve the original entry point and public contracts.

In the site IDE, confirm import, keep the supplied project files, run main.py, save and export. Run comparison_client.py as a separate entry file or copy its calls after the imported definitions when using a single-entry console. Native tests and typing use the full exported project. Keep a baseline export before editing and a separately named improved export after the checks pass.
