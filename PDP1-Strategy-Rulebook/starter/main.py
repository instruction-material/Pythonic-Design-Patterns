from dataclasses import dataclass
from typing import Callable, Iterable


@dataclass(frozen=True)
class LineItem:
	name: str
	price: float
	quantity: int = 1


PricingRule = Callable[[list[LineItem]], float]


def subtotal(items: Iterable[LineItem]) -> float:
	return sum(item.price * item.quantity for item in items)


def standard_total(items: list[LineItem]) -> float:
	return subtotal(items)


def loyalty_total(items: list[LineItem]) -> float:
	return subtotal(items) * 0.9


def bulk_total(items: list[LineItem]) -> float:
	total = subtotal(items)
	quantity = sum(item.quantity for item in items)
	if quantity >= 6:
		total -= 8.0
	return total


RULES: dict[str, PricingRule] = {
	"standard": standard_total,
	"loyalty": loyalty_total,
	"bulk": bulk_total,
}


def checkout_total(items: list[LineItem], rule_name: str) -> float:
	rule = RULES[rule_name]
	return round(rule(items), 2)


def main() -> None:
	cart = [
		LineItem("notebook", 5.0, 2),
		LineItem("pen set", 3.5, 1),
		LineItem("puzzle", 12.0, 3),
	]

	for rule_name in RULES:
		print(f"{rule_name}: ${checkout_total(cart, rule_name):.2f}")


if __name__ == "__main__":
	main()
