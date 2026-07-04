from dataclasses import dataclass
from typing import Iterable, Protocol


#################
#   CONSTANTS   #
#################

DEFAULT_QUANTITY = 1
FULL_PRICE_RATE = 1.0
LOYALTY_PERCENT_OFF = 0.1
BULK_MINIMUM_QUANTITY = 6
BULK_DISCOUNT_AMOUNT = 8.0
CHECKOUT_DECIMAL_PLACES = 2
NOTEBOOK_PRICE = 5.0
NOTEBOOK_QUANTITY = 2
PEN_SET_PRICE = 3.5
PEN_SET_QUANTITY = 1
PUZZLE_PRICE = 12.0
PUZZLE_QUANTITY = 3


#############
#   TYPES   #
#############

# Store one item in the checkout cart
@dataclass(frozen=True)
class LineItem:
	"""Store the product, price, and quantity for one cart line"""

	name: str
	price: float
	quantity: int = DEFAULT_QUANTITY


# Define the callable interface for pricing strategies
class PricingStrategy(Protocol):
	"""Define the pricing strategy interface"""

	def __call__(self, items: list[LineItem]) -> float:
		"""Calculate the total for the provided items"""
		...


# Apply a percentage discount to the whole cart
class LoyaltyDiscount:
	"""Calculate a loyalty discount for repeat customers"""

	def __init__(self, percent_off: float) -> None:
		"""Store the discount percentage"""
		self.percent_off = percent_off

	def __call__(self, items: list[LineItem]) -> float:
		"""Calculate the discounted cart total"""
		return subtotal(items) * (FULL_PRICE_RATE - self.percent_off)


# Apply a fixed discount when the cart has enough items
class BulkBasketDiscount:
	"""Calculate a fixed discount for larger baskets"""

	def __init__(self, minimum_quantity: int, discount_amount: float) -> None:
		"""Store the quantity threshold and discount amount"""
		self.minimum_quantity = minimum_quantity
		self.discount_amount = discount_amount

	def __call__(self, items: list[LineItem]) -> float:
		"""Calculate the bulk-discounted cart total"""
		total = subtotal(items)
		quantity = sum(item.quantity for item in items)

		# Apply the fixed discount only when the basket is large enough
		if quantity >= self.minimum_quantity:
			total -= self.discount_amount

		return total


#################
#   FUNCTIONS   #
#################

def subtotal(items: Iterable[LineItem]) -> float:
	"""Calculate the undiscounted cart subtotal"""
	return sum(item.price * item.quantity for item in items)


def standard_total(items: list[LineItem]) -> float:
	"""Calculate the standard cart total without a discount"""
	return subtotal(items)


def build_rulebook() -> dict[str, PricingStrategy]:
	"""Build the available pricing strategy lookup"""
	return {
		"standard": standard_total,
		"loyalty": LoyaltyDiscount(LOYALTY_PERCENT_OFF),
		"bulk": BulkBasketDiscount(BULK_MINIMUM_QUANTITY, BULK_DISCOUNT_AMOUNT),
	}


def checkout_total(
	items: list[LineItem],
	rule_name: str,
	rulebook: dict[str, PricingStrategy],
) -> float:
	"""Calculate a rounded checkout total using the selected strategy"""
	return round(rulebook[rule_name](items), CHECKOUT_DECIMAL_PLACES)


def build_sample_cart() -> list[LineItem]:
	"""Build the sample cart used by the lesson"""
	return [
		LineItem("notebook", NOTEBOOK_PRICE, NOTEBOOK_QUANTITY),
		LineItem("pen set", PEN_SET_PRICE, PEN_SET_QUANTITY),
		LineItem("puzzle", PUZZLE_PRICE, PUZZLE_QUANTITY),
	]


def main() -> None:
	"""Print totals for every strategy in the rulebook"""
	cart = build_sample_cart()
	rulebook = build_rulebook()

	# Print each rule result in rulebook order
	for rule_name in rulebook:
		print(f"{rule_name}: ${checkout_total(cart, rule_name, rulebook):.2f}")


if __name__ == "__main__":
	main()
