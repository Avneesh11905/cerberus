from typing import Any, AsyncGenerator, Protocol


class EventPublisherPort(Protocol):
    async def publish(self, channel: str, message: dict[str, Any]) -> None:
        """Publishes an event payload to a specific channel."""
        ...


class EventSubscriberPort(Protocol):
    def subscribe(self, channel: str) -> AsyncGenerator[dict[str, Any], None]:
        """Yields events from a specific channel."""
        ...
