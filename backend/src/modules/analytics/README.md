# Analytics Module

This module implements the Analytics & Usage Tracking capability for Cerberus.

## Purpose

The Analytics module tracks metered events for Projects and Tenants (e.g., login attempts, API requests, registrations, OAuth logins, etc.). It provides a decoupled, event-driven mechanism to log events synchronously or asynchronously (via Celery), and then aggregates them for billing, metrics, and usage reporting.

## Architecture

- **Domain**: Defines the `AnalyticsEvent` entity and `EventType` enum.
- **Application**: Contains the `AnalyticsEventPort` and Use Cases like `QueryAnalyticsUseCase`.
- **Infrastructure**: Implements the `SQLAnalyticsRepository`, `AnalyticsEventAdapter` for dispatching events, and Celery tasks (`tasks.py`) for processing and purging old events.

## Features

1. **Per-Project & Per-Tenant Tracking**: Records events tied to specific projects or tenants.
2. **Aggregations**: Celery beat tasks run daily to aggregate raw events into `daily_project_metrics` and `daily_tenant_metrics` tables for fast querying.
3. **Data Purging**: Configurable retention policies auto-purge old events (e.g., API requests > 90 days, security events > 1 year).
