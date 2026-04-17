from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Lead:
	email: str
	source: str
	score: int


def adapt_csv_row(row: dict[str, str]) -> Lead:
	return Lead(
		email=row["email_address"].strip().lower(),
		source="csv",
		score=int(row["score"]),
	)


def adapt_webhook(payload: dict[str, object]) -> Lead:
	return Lead(
		email=str(payload["userEmail"]).strip().lower(),
		source="webhook",
		score=int(payload["priority"]),
	)


def run_pipeline(
	records: list[dict[str, object]],
	adapter: Callable[[dict[str, object]], Lead],
	transform: Callable[[Lead], Lead],
) -> list[Lead]:
	return [transform(adapter(record)) for record in records]


def flag_high_score(lead: Lead) -> Lead:
	if lead.score >= 8:
		return Lead(email=lead.email, source=lead.source, score=10)
	return lead


def main() -> None:
	csv_records = [
		{"email_address": "ADA@example.com", "score": "7"},
		{"email_address": "TURING@example.com", "score": "9"},
	]
	webhook_records = [
		{"userEmail": "hopper@example.com", "priority": 8},
	]

	print(run_pipeline(csv_records, adapt_csv_row, flag_high_score))
	print(run_pipeline(webhook_records, adapt_webhook, flag_high_score))


if __name__ == "__main__":
	main()
