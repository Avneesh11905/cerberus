from uuid import UUID
from pydantic import JsonValue

from src.core.celery_app import celery_app


class CeleryAnalyticsAdapter:
    def record_event(
        self,
        event_type: str,
        event_id: UUID | None = None,
        project_id: UUID | None = None,
        tenant_id: UUID | None = None,
        user_id: UUID | None = None,
        metadata: dict[str, JsonValue] | None = None,
    ) -> None:
        from uuid import uuid4

        kwargs: dict[str, JsonValue] = {
            "event_type": event_type,
            "event_id": str(event_id) if event_id else str(uuid4()),
        }
        if project_id:
            kwargs["project_id"] = str(project_id)
        if tenant_id:
            kwargs["tenant_id"] = str(tenant_id)
        if user_id:
            kwargs["user_id"] = str(user_id)
        if metadata is not None:
            kwargs["metadata"] = metadata

        import warnings

        from celery.exceptions import AlwaysEagerIgnored

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", AlwaysEagerIgnored)
            celery_app.send_task(
                "record_analytics_event", kwargs=kwargs, queue="analytics"
            )
