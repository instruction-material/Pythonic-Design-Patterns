"""A small finite-float pricing model with interchangeable strategies."""
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from math import isfinite

PricingRule = Callable[[list["LineItem"]], float]


def require_amount(value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError("amount must be a number")
    if not isfinite(value) or value < 0:
        raise ValueError("amount must be finite and nonnegative")
    return float(value)


@dataclass(frozen=True)
class LineItem:
    name: str
    price: float
    quantity: int = 1

    def __post_init__(self) -> None:
        if not isinstance(self.name, str):
            raise TypeError("name must be a string")
        if not self.name.strip():
            raise ValueError("name must contain a non-space character")
        require_amount(self.price)
        if not isinstance(self.quantity, int) or isinstance(self.quantity, bool):
            raise TypeError("quantity must be an integer")
        if self.quantity < 0:
            raise ValueError("quantity must be nonnegative")


def subtotal(items: Iterable[LineItem]) -> float:
    total = 0.0
    for item in items:
        if not isinstance(item, LineItem):
            raise TypeError("cart entries must be LineItem values")
        total += item.price * item.quantity
    return require_amount(total)


def standard_total(items: list[LineItem]) -> float:
    return subtotal(items)


def loyalty_total(items: list[LineItem]) -> float:
    return subtotal(items) * 0.9


def bulk_total(items: list[LineItem]) -> float:
    total = subtotal(items)
    return max(0.0, total - 8.0) if sum(i.quantity for i in items) >= 6 else total


def register_rule(rules: dict[str, PricingRule], name: str, rule: PricingRule) -> None:
    if not isinstance(name, str):
        raise TypeError("name must be a string")
    if not name.strip():
        raise ValueError("name must contain a non-space character")
    if not callable(rule):
        raise TypeError("rule must be callable")
    if name in rules:
        raise ValueError("duplicate rule")
    rules[name] = rule


def build_rulebook() -> dict[str, PricingRule]:
    return {"standard": standard_total, "loyalty": loyalty_total, "bulk": bulk_total}


RULES = build_rulebook()


def checkout_total(items: list[LineItem], rule_name: str,
                   rulebook: Mapping[str, PricingRule] | None = None) -> float:
    """Preserve the caller's list, call once, then round the final valid amount."""
    if not isinstance(rule_name, str):
        raise TypeError("rule name must be a string")
    cart = list(items)
    subtotal(cart)
    rule = (RULES if rulebook is None else rulebook)[rule_name]
    if not callable(rule):
        raise TypeError("rule must be callable")
    return round(require_amount(rule(cart)), 2)


def build_sample_cart() -> list[LineItem]:
    return [LineItem("notebook", 5.0, 2), LineItem("pen set", 3.5),
            LineItem("puzzle", 12.0, 3)]


def main() -> None:
    cart = build_sample_cart()
    for name in RULES:
        print(f"{name}: ${checkout_total(cart, name):.2f}")


if __name__ == "__main__":
    main()
