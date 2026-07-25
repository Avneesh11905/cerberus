from typing import Protocol
from collections.abc import AsyncGenerator, Mapping
from pydantic import JsonValue


class EventPublisherPort(Protocol):
    async def publish(self, channel: str, message: Mapping[str, JsonValue]) -> None:
        """Publishes an event payload to a specific channel."""
        ...


class EventSubscriberPort(Protocol):
    def subscribe(self, channel: str) -> AsyncGenerator[dict[str, JsonValue]]:
        """Yields events from a specific channel."""
        ...
