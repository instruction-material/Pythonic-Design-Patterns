"""Versioned vendor records translated into a small, immutable internal model."""
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass


class AdapterError(ValueError):
    """An external record cannot be translated into a Lead."""


class IntegrationError(RuntimeError):
    """The injected vendor reader failed before records could be adapted."""


def normalized_email(value: object) -> str:
    if not isinstance(value, str):
        raise TypeError("email must be text")
    email = value.strip().lower()
    if (email.count("@") != 1 or any(c.isspace() for c in email)
            or not all(email.split("@"))):
        raise ValueError("email requires nonempty local and domain parts")
    return email


def score_value(value: object, *, csv: bool = False) -> int:
    if csv and isinstance(value, str):
        clean = value.strip()
        if not clean or any(c not in "0123456789" for c in clean):
            raise ValueError("CSV score must contain decimal digits")
        value = int(clean)
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError("score must be an integer")
    if not 0 <= value <= 10:
        raise ValueError("score must be between zero and ten")
    return value


@dataclass(frozen=True)
class Lead:
    email: str
    source: str
    score: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "email", normalized_email(self.email))
        if not isinstance(self.source, str) or not self.source.strip():
            raise ValueError("source must be nonblank text")
        score_value(self.score)


def record(value: object) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise TypeError("record must be a mapping")
    if any(not isinstance(k, str) for k in value):
        raise TypeError("record keys must be text")
    return value


def version(value: Mapping[str, object], *, csv: bool = False) -> int:
    raw = value.get("version", 1)
    if csv and raw in ("1", "2"):
        raw = int(str(raw))
    if type(raw) is not int:
        raise TypeError("version must be an integer")
    if raw not in (1, 2):
        raise ValueError("unsupported record version")
    return raw


def adapt_csv_row(row: Mapping[str, object]) -> Lead:
    try:
        source = record(row)
        v = version(source, csv=True)
        email_key, score_key = ("email_address", "score") if v == 1 else ("contact_email", "lead_score")
        return Lead(normalized_email(source[email_key]), "csv",
                    score_value(source.get(score_key, 0), csv=True))
    except (KeyError, TypeError, ValueError) as error:
        raise AdapterError("invalid CSV lead") from error


def adapt_webhook(payload: Mapping[str, object]) -> Lead:
    try:
        source = record(payload)
        if version(source) == 1:
            email, score = source["userEmail"], source.get("priority", 0)
        else:
            contact = record(source["contact"])
            ranking = record(source.get("ranking", {}))
            email, score = contact["email"], ranking.get("score", 0)
        return Lead(normalized_email(email), "webhook", score_value(score))
    except (KeyError, TypeError, ValueError) as error:
        raise AdapterError("invalid webhook lead") from error


def flag_high_score(lead: Lead) -> Lead:
    if not isinstance(lead, Lead):
        raise TypeError("transform requires a Lead")
    return Lead(lead.email, lead.source, 10) if lead.score >= 8 else lead


def run_pipeline(records: Iterable[Mapping[str, object]],
                 adapter: Callable[[Mapping[str, object]], Lead],
                 transform: Callable[[Lead], Lead]) -> list[Lead]:
    if not callable(adapter) or not callable(transform):
        raise TypeError("adapter and transform must be callable")
    result = []
    for raw in records:
        lead = adapter(raw)
        if not isinstance(lead, Lead):
            raise TypeError("adapter must return a Lead")
        transformed = transform(lead)
        if not isinstance(transformed, Lead):
            raise TypeError("transform must return a Lead")
        result.append(transformed)
    return result


class LeadImportTemplate:
    source_name = "unknown"

    def adapt(self, value: Mapping[str, object]) -> Lead:
        raise NotImplementedError("choose an external record adapter")

    def transform(self, lead: Lead) -> Lead:
        return flag_high_score(lead)

    def run(self, records: Iterable[Mapping[str, object]]) -> list[Lead]:
        return run_pipeline(records, self.adapt, self.transform)


class CsvLeadImporter(LeadImportTemplate):
    source_name = "csv"
    def adapt(self, value: Mapping[str, object]) -> Lead:
        return adapt_csv_row(value)


class WebhookLeadImporter(LeadImportTemplate):
    source_name = "webhook"
    def adapt(self, value: Mapping[str, object]) -> Lead:
        return adapt_webhook(value)


def fetch_leads(fetch: Callable[[], Iterable[Mapping[str, object]]],
                adapter: Callable[[Mapping[str, object]], Lead],
                transform: Callable[[Lead], Lead] = flag_high_score) -> list[Lead]:
    try:
        # Materialize here so iteration-time I/O failures retain the same boundary.
        rows = tuple(fetch())
    except OSError as error:
        raise IntegrationError("vendor lead reader failed") from error
    return run_pipeline(rows, adapter, transform)


def build_csv_records() -> list[dict[str, object]]:
    return [{"email_address": "ADA@example.com", "score": "7"},
            {"email_address": "TURING@example.com", "score": "9"}]


def build_webhook_records() -> list[dict[str, object]]:
    return [{"userEmail": "hopper@example.com", "priority": 8}]


def main() -> None:
    csv_rows, webhook_rows = build_csv_records(), build_webhook_records()
    print("csv:", CsvLeadImporter().run(csv_rows))
    print("webhook:", WebhookLeadImporter().run(webhook_rows))
    print("functional equal:", run_pipeline(csv_rows, adapt_csv_row, flag_high_score)
          == CsvLeadImporter().run(csv_rows))


if __name__ == "__main__":
    main()
