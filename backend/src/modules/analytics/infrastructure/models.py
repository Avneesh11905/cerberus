import uuid
from typing import Any

from sqlalchemy import Column, Date, DateTime, Enum, Integer, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID

from src.core.database import Base
from src.shared.domain.enums import EventType


class AnalyticsEventModel(Base):
    __tablename__ = "analytics_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    event_type: Any = Column(
        Enum(EventType, name="event_type_enum"), nullable=False, index=True
    )
    timestamp = Column(
        DateTime(timezone=True), default=func.now(), nullable=False, index=True
    )
    metadata_payload = Column(JSONB, nullable=True)


class DailyProjectMetricModel(Base):
    __tablename__ = "daily_project_metrics"
    __table_args__ = (UniqueConstraint("project_id", "date", name="uq_project_date"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    date = Column(Date, nullable=False)
    api_requests = Column(Integer, default=0, nullable=False)
    login_successes = Column(Integer, default=0, nullable=False)
    login_failures = Column(Integer, default=0, nullable=False)
    registrations = Column(Integer, default=0, nullable=False)
    active_users = Column(Integer, default=0, nullable=False)


class DailyTenantMetricModel(Base):
    __tablename__ = "daily_tenant_metrics"
    __table_args__ = (UniqueConstraint("tenant_id", "date", name="uq_tenant_date"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    date = Column(Date, nullable=False)
    api_requests = Column(Integer, default=0, nullable=False)
    login_successes = Column(Integer, default=0, nullable=False)
    login_failures = Column(Integer, default=0, nullable=False)
    registrations = Column(Integer, default=0, nullable=False)
    active_users = Column(Integer, default=0, nullable=False)
