"""PDP9 compares extension forms without changing the PDP8 adapter schema."""
from main import (CsvLeadImporter, WebhookLeadImporter, Lead, adapt_csv_row,
                  adapt_webhook, build_csv_records, build_webhook_records,
                  flag_high_score, run_pipeline)


def keep_score(lead: Lead) -> Lead:
    return lead


class KeepCsvScore(CsvLeadImporter):
    def transform(self, lead: Lead) -> Lead:
        return keep_score(lead)


def comparison_main() -> None:
    csv_rows = build_csv_records()
    webhook_rows = build_webhook_records()
    print("csv forms equal:", CsvLeadImporter().run(csv_rows)
          == run_pipeline(csv_rows, adapt_csv_row, flag_high_score))
    print("webhook forms equal:", WebhookLeadImporter().run(webhook_rows)
          == run_pipeline(webhook_rows, adapt_webhook, flag_high_score))
    functional = run_pipeline(csv_rows, adapt_csv_row, keep_score)
    print("replacement scores:", [lead.score for lead in functional])
    print("replacement equal:", functional == KeepCsvScore().run(csv_rows))


if __name__ == "__main__":
    comparison_main()
