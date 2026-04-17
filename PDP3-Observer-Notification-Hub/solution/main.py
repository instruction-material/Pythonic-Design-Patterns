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
		self._listeners: dict[str, dict[int, Listener]] = defaultdict(dict)
		self._next_token = 1

	def subscribe(self, event_name: str, listener: Listener) -> int:
		token = self._next_token
		self._next_token += 1
		self._listeners[event_name][token] = listener
		return token

	def unsubscribe(self, event_name: str, token: int) -> None:
		self._listeners[event_name].pop(token, None)

	def publish(self, event_name: str, event: OrderEvent) -> None:
		for listener in list(self._listeners[event_name].values()):
			listener(event)


def print_summary(event: OrderEvent) -> None:
	print(f"summary: {event.order_id} -> {event.status}")


def print_email(event: OrderEvent) -> None:
	print(f"email: sent {event.status} message to {event.customer_email}")


def audit_log(event: OrderEvent) -> None:
	print(f"audit: order={event.order_id} status={event.status}")


def main() -> None:
	bus = EventBus()
	summary_token = bus.subscribe("order.updated", print_summary)
	bus.subscribe("order.updated", print_email)
	bus.subscribe("order.updated", audit_log)

	bus.publish("order.updated", OrderEvent("A-102", "shipped", "ada@example.com"))
	bus.unsubscribe("order.updated", summary_token)
	bus.publish("order.updated", OrderEvent("A-102", "delivered", "ada@example.com"))


if __name__ == "__main__":
	main()
