import uuid
from sqlalchemy import Column, Date, DateTime, Enum, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB, UUID

from src.core.database import Base
from src.shared.domain.enums import EventType


class AnalyticsEventModel(Base):
    __tablename__ = "analytics_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    event_type: Mapped[EventType] = mapped_column(
        Enum(EventType, name="event_type_enum", native_enum=True),
        nullable=False,
        index=True,
    )
    timestamp = Column(
        DateTime(timezone=True), default=func.now(), nullable=False, index=True
    )
    metadata_payload = Column(JSONB, nullable=True)


class LiveProjectMetricModel(Base):
    """Real-time per-day project metrics. Kept continuously up-to-date via UPSERT on every event."""

    __tablename__ = "live_project_metrics"
    __table_args__ = (
        UniqueConstraint("project_id", "date", name="uq_live_project_date"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    date = Column(Date, nullable=False)
    api_requests = Column(Integer, default=0, nullable=False)
    login_successes = Column(Integer, default=0, nullable=False)
    login_failures = Column(Integer, default=0, nullable=False)
    registrations = Column(Integer, default=0, nullable=False)
    active_users = Column(Integer, default=0, nullable=False)
    emails_sent = Column(Integer, default=0, nullable=False)
    emails_failed = Column(Integer, default=0, nullable=False)


class LiveTenantMetricModel(Base):
    """Real-time per-day tenant metrics. Kept continuously up-to-date via UPSERT on every event."""

    __tablename__ = "live_tenant_metrics"
    __table_args__ = (
        UniqueConstraint("tenant_id", "date", name="uq_live_tenant_date"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    date = Column(Date, nullable=False)
    api_requests = Column(Integer, default=0, nullable=False)
    login_successes = Column(Integer, default=0, nullable=False)
    login_failures = Column(Integer, default=0, nullable=False)
    registrations = Column(Integer, default=0, nullable=False)
    active_users = Column(Integer, default=0, nullable=False)
    emails_sent = Column(Integer, default=0, nullable=False)
    emails_failed = Column(Integer, default=0, nullable=False)
    projects_created = Column(Integer, default=0, nullable=False)


class LiveSystemMetricModel(Base):
    """Real-time per-day system-level metrics. Kept continuously up-to-date via UPSERT on every event."""

    __tablename__ = "live_system_metrics"
    __table_args__ = (UniqueConstraint("date", name="uq_live_system_date"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date = Column(Date, nullable=False, index=True)
    tenants_onboarded = Column(Integer, default=0, nullable=False)
    tenant_suspensions = Column(Integer, default=0, nullable=False)
    api_key_rotations = Column(Integer, default=0, nullable=False)
    jwt_key_rotations = Column(Integer, default=0, nullable=False)
