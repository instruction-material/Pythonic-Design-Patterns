from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


#################
#   CONSTANTS   #
#################

UNKNOWN_SOURCE_NAME = "unknown"
CSV_SOURCE_NAME = "csv"
WEBHOOK_SOURCE_NAME = "webhook"
HIGH_SCORE_THRESHOLD = 8
MAXIMUM_SCORE = 10
CSV_EMAIL_FIELD = "email_address"
CSV_SCORE_FIELD = "score"
WEBHOOK_EMAIL_FIELD = "userEmail"
WEBHOOK_PRIORITY_FIELD = "priority"


#############
#   TYPES   #
#############

# Store one normalized lead after import
@dataclass(frozen=True)
class Lead:
	"""Store email, source, and score for one lead"""

	email: str
	source: str
	score: int


# Define the template method for importing leads
class LeadImportTemplate:
	"""Adapt records and run shared lead transformations"""

	source_name = UNKNOWN_SOURCE_NAME

	def adapt(self, record: dict[str, object]) -> Lead:
		"""Convert one source record into a lead"""
		raise NotImplementedError

	def transform(self, lead: Lead) -> Lead:
		"""Apply shared lead transformations"""
		return flag_high_score(lead)

	def run(self, records: list[dict[str, object]]) -> list[Lead]:
		"""Adapt and transform every source record"""
		return [self.transform(self.adapt(record)) for record in records]


# Adapt CSV-shaped records into leads
class CsvLeadImporter(LeadImportTemplate):
	"""Import leads from CSV-style field names"""

	source_name = CSV_SOURCE_NAME

	def adapt(self, record: dict[str, object]) -> Lead:
		"""Convert one CSV record into a lead"""
		return Lead(
			email=str(record[CSV_EMAIL_FIELD]).strip().lower(),
			source=self.source_name,
			score=int(record[CSV_SCORE_FIELD]),
		)


# Adapt webhook-shaped records into leads
class WebhookLeadImporter(LeadImportTemplate):
	"""Import leads from webhook-style field names"""

	source_name = WEBHOOK_SOURCE_NAME

	def adapt(self, record: dict[str, object]) -> Lead:
		"""Convert one webhook record into a lead"""
		return Lead(
			email=str(record[WEBHOOK_EMAIL_FIELD]).strip().lower(),
			source=self.source_name,
			score=int(record[WEBHOOK_PRIORITY_FIELD]),
		)


#################
#   FUNCTIONS   #
#################

def flag_high_score(lead: Lead) -> Lead:
	"""Raise high-scoring leads to the maximum score"""
	# Promote leads that meet the high-score threshold
	if lead.score >= HIGH_SCORE_THRESHOLD:
		return Lead(email=lead.email, source=lead.source, score=MAXIMUM_SCORE)

	return lead


def run_pipeline(
	records: list[dict[str, object]],
	adapter: Callable[[dict[str, object]], Lead],
	transform: Callable[[Lead], Lead],
) -> list[Lead]:
	"""Run a functional adapter and transform pipeline"""
	return [transform(adapter(record)) for record in records]


def adapt_csv_row(row: dict[str, object]) -> Lead:
	"""Adapt one CSV row using the class-based importer"""
	return CsvLeadImporter().adapt(row)


def build_csv_records() -> list[dict[str, object]]:
	"""Build sample CSV records for the lesson"""
	return [
		{CSV_EMAIL_FIELD: "ADA@example.com", CSV_SCORE_FIELD: "7"},
		{CSV_EMAIL_FIELD: "TURING@example.com", CSV_SCORE_FIELD: "9"},
	]


def build_webhook_records() -> list[dict[str, object]]:
	"""Build sample webhook records for the lesson"""
	return [
		{WEBHOOK_EMAIL_FIELD: "hopper@example.com", WEBHOOK_PRIORITY_FIELD: 8},
	]


def main() -> None:
	"""Run class-based and function-based import pipelines"""
	csv_records = build_csv_records()
	webhook_records = build_webhook_records()

	print(CsvLeadImporter().run(csv_records))
	print(WebhookLeadImporter().run(webhook_records))
	print(run_pipeline(csv_records, adapt_csv_row, flag_high_score))


if __name__ == "__main__":
	main()
