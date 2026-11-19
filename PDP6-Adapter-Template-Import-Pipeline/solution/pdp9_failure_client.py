"""PDP9 exposes ordered short-circuit behavior through both extension forms."""
from collections.abc import Mapping
from main import Lead, LeadImportTemplate, adapt_csv_row, run_pipeline


def failure_main() -> None:
    rows: list[dict[str, object]] = [
        {"email_address": "first@example.com"},
        {"email_address": "second@example.com"},
        {"email_address": "third@example.com"},
    ]
    for form in ("class", "callable"):
        events: list[str] = []
        failure = RuntimeError("second transform")

        def adapt(row: Mapping[str, object]) -> Lead:
            value = adapt_csv_row(row)
            events.append("adapt:" + value.email.split("@")[0])
            return value

        def transform(value: Lead) -> Lead:
            name = value.email.split("@")[0]
            events.append("transform:" + name)
            if name == "second":
                raise failure
            return value

        class TracedImporter(LeadImportTemplate):
            def adapt(self, row: Mapping[str, object]) -> Lead:
                return adapt(row)

            def transform(self, value: Lead) -> Lead:
                return transform(value)

        try:
            if form == "class":
                TracedImporter().run(rows)
            else:
                run_pipeline(rows, adapt, transform)
        except RuntimeError as error:
            print(form + " same failure:", error is failure)
            print(form + " events:", events)


if __name__ == "__main__":
    failure_main()
