from collections import defaultdict
from dataclasses import dataclass
from typing import Callable

#################
#   CONSTANTS   #
#################

INITIAL_LISTENER_TOKEN = 1
ORDER_UPDATED_EVENT = "order.updated"
SAMPLE_ORDER_ID = "A-102"
SHIPPED_STATUS = "shipped"
DELIVERED_STATUS = "delivered"
SAMPLE_CUSTOMER_EMAIL = "ada@example.com"


#############
#   TYPES   #
#############


# Store one order event sent through the bus
@dataclass(frozen=True)
class OrderEvent:
    """Store order update data for listeners"""

    order_id: str
    status: str
    customer_email: str


listener = Callable[[OrderEvent], None]


# Manage subscriptions and event publication
class EventBus:
    """Store listeners and publish events by name"""

    def __init__(self) -> None:
        """Initialize an empty listener registry"""
        self._listeners: dict[str, dict[int, listener]] = defaultdict(dict)
        self._next_token = INITIAL_LISTENER_TOKEN

    def subscribe(self, event_name: str, listener: listener) -> int:
        """Subscribe a listener and return its token"""
        token = self._next_token
        self._next_token += 1
        self._listeners[event_name][token] = listener
        return token

    def unsubscribe(self, event_name: str, token: int) -> None:
        """Remove a listener token from an event"""
        self._listeners[event_name].pop(token, None)

    def publish(self, event_name: str, event: OrderEvent) -> None:
        """Publish an event to every subscribed listener"""
        # Copy listeners before publishing so callbacks can safely unsubscribe
        for listener in list(self._listeners[event_name].values()):
            listener(event)


#################
#   FUNCTIONS   #
#################


def print_summary(event: OrderEvent) -> None:
    """Print a compact order update summary"""
    print(f"summary: {event.order_id} -> {event.status}")


def print_email(event: OrderEvent) -> None:
    """Print the email notification that would be sent"""
    print(f"email: sent {event.status} message to {event.customer_email}")


def audit_log(event: OrderEvent) -> None:
    """Print an audit entry for the order update"""
    print(f"audit: order={event.order_id} status={event.status}")


def build_order_event(status: str) -> OrderEvent:
    """Build the sample order event for one status"""
    return OrderEvent(SAMPLE_ORDER_ID, status, SAMPLE_CUSTOMER_EMAIL)


def main() -> None:
    """Subscribe listeners and publish sample order events"""
    bus = EventBus()
    summary_token = bus.subscribe(ORDER_UPDATED_EVENT, print_summary)
    bus.subscribe(ORDER_UPDATED_EVENT, print_email)
    bus.subscribe(ORDER_UPDATED_EVENT, audit_log)

    bus.publish(ORDER_UPDATED_EVENT, build_order_event(SHIPPED_STATUS))
    bus.unsubscribe(ORDER_UPDATED_EVENT, summary_token)
    bus.publish(ORDER_UPDATED_EVENT, build_order_event(DELIVERED_STATUS))


if __name__ == "__main__":
    main()
