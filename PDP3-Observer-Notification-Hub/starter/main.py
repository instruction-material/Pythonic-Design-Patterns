from collections import defaultdict
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class OrderEvent:
	order_id: str
	status: str
	customer_email: str


Listener = Callable[[OrderEvent], None]


class EventBus:
	def __init__(self) -> None:
		self._listeners: dict[str, list[Listener]] = defaultdict(list)

	def subscribe(self, event_name: str, listener: Listener) -> None:
		self._listeners[event_name].append(listener)

	def publish(self, event_name: str, event: OrderEvent) -> None:
		for listener in self._listeners[event_name]:
			listener(event)


def print_summary(event: OrderEvent) -> None:
	print(f"summary: {event.order_id} -> {event.status}")


def print_email(event: OrderEvent) -> None:
	print(f"email: sent {event.status} message to {event.customer_email}")


def main() -> None:
	bus = EventBus()
	bus.subscribe("order.updated", print_summary)
	bus.subscribe("order.updated", print_email)
	bus.publish("order.updated", OrderEvent("A-102", "shipped", "ada@example.com"))


if __name__ == "__main__":
	main()
