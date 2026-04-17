from dataclasses import dataclass
from typing import Iterable, Protocol


@dataclass(frozen=True)
class LineItem:
	name: str
	price: float
	quantity: int = 1


def subtotal(items: Iterable[LineItem]) -> float:
	return sum(item.price * item.quantity for item in items)


class PricingStrategy(Protocol):
	def __call__(self, items: list[LineItem]) -> float: ...


def standard_total(items: list[LineItem]) -> float:
	return subtotal(items)


class LoyaltyDiscount:
	def __init__(self, percent_off: float) -> None:
		self.percent_off = percent_off

	def __call__(self, items: list[LineItem]) -> float:
		return subtotal(items) * (1.0 - self.percent_off)


class BulkBasketDiscount:
	def __init__(self, minimum_quantity: int, discount_amount: float) -> None:
		self.minimum_quantity = minimum_quantity
		self.discount_amount = discount_amount

	def __call__(self, items: list[LineItem]) -> float:
		total = subtotal(items)
		quantity = sum(item.quantity for item in items)
		if quantity >= self.minimum_quantity:
			total -= self.discount_amount
		return total


def build_rulebook() -> dict[str, PricingStrategy]:
	return {
		"standard": standard_total,
		"loyalty": LoyaltyDiscount(0.1),
		"bulk": BulkBasketDiscount(6, 8.0),
	}


def checkout_total(
	items: list[LineItem],
	rule_name: str,
	rulebook: dict[str, PricingStrategy],
) -> float:
	return round(rulebook[rule_name](items), 2)


def main() -> None:
	cart = [
		LineItem("notebook", 5.0, 2),
		LineItem("pen set", 3.5, 1),
		LineItem("puzzle", 12.0, 3),
	]
	rulebook = build_rulebook()

	for rule_name in rulebook:
		print(f"{rule_name}: ${checkout_total(cart, rule_name, rulebook):.2f}")


if __name__ == "__main__":
	main()
