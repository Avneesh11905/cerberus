# ⚙️ Shared Infrastructure

The `shared` module contains the cross-cutting concerns and foundational infrastructure used by all other modules in the Cerberus platform.

## 🏗️ Components

- **`api/`**: Global FastAPI dependencies, CORS middleware, rate-limiting, cookie helpers, CSRF utilities, and shared routes (health check, dev email preview).
- **`adapters/`**: Concrete implementations of shared ports:
  - `api_key.py` — SHA-256 API key hashing and generation (`ApiKeyAdapter`)
  - `rsa_key.py` — Async RSA-2048 keypair generation (`RsaKeyAdapter`)
  - `cache/` — Redis-backed cache adapter (`RedisCacheAdapter`)
  - `email_client.py` — Resend transactional email client (`ResendEmailClient`)
  - `encryption.py` — Fernet symmetric encryption adapter (`FernetEncryptionAdapter`)
  - `logger.py` — Async SQL logger that batches log entries via Celery (`AsyncSQLLogger`)
  - `task_runner/` — Celery task dispatcher (`CeleryTaskRunner`)
- **`core/ports/`**: `typing.Protocol` interfaces for all shared adapters (`ApiKeyPort`, `RsaKeyPort`, `CachePort`, `EncryptionPort`, `EmailClientPort`, etc.).
- **`infrastructure/`**:
  - `sql/uow.py` — `SQLAlchemyUnitOfWork` and `get_uow` FastAPI dependency.
  - `tasks.py` — Celery tasks for log batch insertion and old log cleanup.
- **`templates/`**: Jinja2 HTML email templates used by the auth email sender and the dev preview route.
