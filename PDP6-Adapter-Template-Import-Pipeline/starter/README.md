# Adapter and Import Pipeline

Python 3.14. Refactor the working run_pipeline loop into a small checked mapping helper and a callable pipeline, preserving its public contracts and exact output. Compare that functional boundary with LeadImportTemplate, CsvLeadImporter and WebhookLeadImporter. Both original public adapters, adapt_csv_row and adapt_webhook, remain available.

Lead is an immutable internal record with email, source and score. Email is trimmed and lowercased; this teaching contract requires exactly one @, nonempty parts and no whitespace, without claiming full email-address validation. Scores are integers 0..10 and exclude bool. flag_high_score maps scores >=8 to 10 and preserves lower scores. Raw vendor dictionaries are never retained in Lead.

CSV version defaults to 1 and supports integer 1/2 or CSV text "1"/"2". Version 1 requires email_address and defaults missing score to 0. Version 2 requires contact_email and defaults missing lead_score to 0. CSV scores accept integers or trimmed decimal-digit text. Webhook version defaults to integer 1; version 1 requires userEmail and defaults missing priority to 0. Version 2 requires contact.email; ranking may be omitted and ranking.score defaults to 0. Present malformed nested records are rejected. Webhook scores accept integers only. Both adapters ignore unknown fields, reject unknown versions, preserve source labels csv/webhook and raise AdapterError with the original KeyError/TypeError/ValueError as cause.

run_pipeline accepts an iterable plus adapter and transform callables, preserves order and fails at the first error. Both callables must return Lead. Empty input produces an empty list, with callable configuration still validated. It returns a list only after success; local partial lists are not returned, but an input iterator may have been consumed and external callback effects cannot be undone. Arbitrary callback exceptions propagate unchanged.

fetch_leads receives an injected zero-argument reader, materializes its iterable at the boundary and maps call-time or iteration-time OSError (including TimeoutError) to IntegrationError while retaining the cause. Programming errors propagate. No network service is needed. Core Lead has no timestamp or physical-unit fields; the separate measurement practice supplies those conversions and an explicit export round-trip contract.

Run `python3.14 -B main.py` and `python3.14 -B -m unittest discover -s . -p test_contract.py -v`. The 10 public behavioral groups pass in both roles before refactoring. Development pins can be installed with `python3.14 -m pip install -r requirements-dev.txt`; runtime code uses the standard library.

Default output:

```text
csv: [Lead(email='ada@example.com', source='csv', score=7), Lead(email='turing@example.com', source='csv', score=10)]
webhook: [Lead(email='hopper@example.com', source='webhook', score=10)]
functional equal: True
```
