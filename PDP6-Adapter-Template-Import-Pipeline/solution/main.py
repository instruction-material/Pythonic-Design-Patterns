from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Lead:
	email: str
	source: str
	score: int


def flag_high_score(lead: Lead) -> Lead:
	if lead.score >= 8:
		return Lead(email=lead.email, source=lead.source, score=10)
	return lead


class LeadImportTemplate:
	source_name = "unknown"

	def adapt(self, record: dict[str, object]) -> Lead:
		raise NotImplementedError

	def transform(self, lead: Lead) -> Lead:
		return flag_high_score(lead)

	def run(self, records: list[dict[str, object]]) -> list[Lead]:
		return [self.transform(self.adapt(record)) for record in records]


class CsvLeadImporter(LeadImportTemplate):
	source_name = "csv"

	def adapt(self, record: dict[str, object]) -> Lead:
		return Lead(
			email=str(record["email_address"]).strip().lower(),
			source=self.source_name,
			score=int(record["score"]),
		)


class WebhookLeadImporter(LeadImportTemplate):
	source_name = "webhook"

	def adapt(self, record: dict[str, object]) -> Lead:
		return Lead(
			email=str(record["userEmail"]).strip().lower(),
			source=self.source_name,
			score=int(record["priority"]),
		)


def run_pipeline(
	records: list[dict[str, object]],
	adapter: Callable[[dict[str, object]], Lead],
	transform: Callable[[Lead], Lead],
) -> list[Lead]:
	return [transform(adapter(record)) for record in records]


def adapt_csv_row(row: dict[str, object]) -> Lead:
	return CsvLeadImporter().adapt(row)


def main() -> None:
	csv_records = [
		{"email_address": "ADA@example.com", "score": "7"},
		{"email_address": "TURING@example.com", "score": "9"},
	]
	webhook_records = [
		{"userEmail": "hopper@example.com", "priority": 8},
	]

	print(CsvLeadImporter().run(csv_records))
	print(WebhookLeadImporter().run(webhook_records))
	print(run_pipeline(csv_records, adapt_csv_row, flag_high_score))


if __name__ == "__main__":
	main()
