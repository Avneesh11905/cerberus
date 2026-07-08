# ⚙️ Shared Infrastructure

The `shared` domain contains the cross-cutting concerns and foundational infrastructure utilized by all other domains in the Cerberus platform.

## 🏗️ Components
- **API (`api/`)**: Global dependencies, exception handlers, rate-limiting (`limiter`), and utility functions.
- **Config (`config/`)**: Centralized Pydantic settings loading `.env` variables for database, caching, tokens, and email.
- **Core (`core/`)**: Domain primitives, custom exceptions (`ResourceNotFound`, `UnauthorizedException`), and event buses.
- **Infrastructure (`infrastructure/`)**:
  - `sql/`: SQLAlchemy declarative base, database sessions, and the `SQLAlchemyUnitOfWork`.
  - `cache/`: Redis client initialization and pooling.
  - `email/`: Resend API client for dispatching transactional emails.
  - `task_runner/`: Celery application and worker configurations.
