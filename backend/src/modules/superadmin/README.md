# 🛡️ Admin Domain

The `admin` domain is responsible for system-wide health monitoring, logging, and tenant management. This module is strictly protected and only accessible to Global Administrators.

## 🏗️ Architecture
This domain follows the Hexagonal Architecture pattern:
- **API (`api/`)**: Exposes FastAPI endpoints for health checks and tenant controls. Protected by `require_global_admin` dependencies.
- **Core (`core/`)**: Contains pure business logic for administrative actions (e.g., banning a tenant, auditing system logs).
- **Adapters (`adapters/`)**: Integrates with external logging and monitoring systems.

## 🔐 Security
All routes within this domain must validate that the incoming request contains a valid `X-Cerberus-Admin-Key` or that the authenticated user possesses the `Global Admin` role.
