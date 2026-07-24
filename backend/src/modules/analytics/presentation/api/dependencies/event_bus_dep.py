from src.core.container import app_container
from src.shared.application.ports.event_bus import EventSubscriberPort
from src.shared.presentation.api.dependencies import Depends
from typing import Annotated


def get_event_subscriber() -> EventSubscriberPort:
    return app_container.event_subscriber_adapter


EventSubscriberPortDep = Annotated[EventSubscriberPort, Depends(get_event_subscriber)]
