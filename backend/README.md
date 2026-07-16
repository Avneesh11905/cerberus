<div align="center">
  <h1>🛡️ Cerberus - Auth-as-a-Service Backend</h1>
  <p>A strictly typed, production-grade identity platform built with FastAPI.</p>
</div>

---

## 📖 Introduction
**Cerberus** is a complete, self-hosted identity backend. It provides **Auth-as-a-Service**, allowing you to create isolated **Projects** for your applications, configure dynamic OAuth providers, manage environments (Development/Production), and securely manage your end-users.

It is designed with security and production-readiness in mind, featuring:
- **True Multi-Project Isolation:** A hierarchical RBAC system with Global Admins, Dashboard Users, and End-Users scoped to Projects.
- **Dynamic OAuth per Project:** You can bring your own OAuth credentials (Google, GitHub) for each project.
- **Dynamic CORS & Environment Modes:** Instantly toggle rate limits and allow local testing across your frontend without touching code.
- **Strict Type Safety:** Enforcement of core domain models like `UUID` and `EmailStr` across all boundaries.
- **Advanced Session Management:** A dual-token architecture (HttpOnly Refresh Cookies + JWT Access Tokens) with lazy token rotation, session families, and remote device revocation.
- **Distributed Background Processing:** Production-ready background tasks using Celery and Redis to handle email dispatches and periodic cleanups asynchronously.
- **Centralized Dependency Injection:** All infrastructure singletons (repositories, use cases, adapters) are wired in a single `AppContainer` at `src/core/container.py`.

> **Infrastructure Independence:** Out of the box, this platform is **SQL-based** (using SQLAlchemy & Alembic), but because the system is deeply modular, you are not locked in! You can easily swap out the SQL database, cache, or email provider by writing a new adapter.

---

## 📑 Table of Contents
- [1. 🏗️ Architecture Overview](#1-️-architecture-overview)
  - [1.1 The Modules](#11-the-modules)
  - [1.2 Inside Each Module (Hexagonal Layers)](#12-inside-each-module-hexagonal-layers)
  - [1.3 Dependency Injection (AppContainer)](#13-dependency-injection-appcontainer)
  - [1.4 Transaction Management (Unit of Work)](#14-transaction-management-unit-of-work)
- [2. 🏢 Project Management](#2--project-management)
  - [2.1 Roles](#21-roles)
  - [2.2 Project Management & Environments](#22-project-management--environments)
  - [2.3 Dynamic CORS Origins](#23-dynamic-cors-origins)
- [3. 🚀 Getting Started](#3--getting-started)
  - [3.1 Prerequisites](#31-prerequisites)
  - [3.2 Setup Instructions](#32-setup-instructions)
- [4. ⚙️ Environment Variables Guide](#4-️-environment-variables-guide)
  - [4.1 General & Security](#41-general--security)
  - [4.2 Infrastructure](#42-infrastructure)
  - [4.3 Email Provider](#43-email-provider)
  - [4.4 Token, Verification & Rate Limiting](#44-token-verification--rate-limiting)
- [5. 🔄 Authentication Workflows](#5--authentication-workflows)
  - [5.1 Local Registration](#51-local-registration)
  - [5.2 Login & Session Issuance (Local)](#52-login--session-issuance-local)
  - [5.3 Login & Session Issuance (OAuth)](#53-login--session-issuance-oauth)
  - [5.4 Session Rotation](#54-session-rotation)
  - [5.5 Logout & Session Revocation](#55-logout--session-revocation)
  - [5.6 Security Alerts & Anomaly Detection](#56-security-alerts--anomaly-detection)
- [6. 💻 Frontend Integration Guidelines](#6--frontend-integration-guidelines)
  - [6.1 Required Frontend Routes](#61-required-frontend-routes)
  - [6.2 API Reference Checklist](#62-api-reference-checklist)
  - [6.3 Handling Token Rotation (Axios Example)](#63-handling-token-rotation-axios-example)
  - [6.4 CSRF Protection Details](#64-csrf-protection-details)
- [7. 🛠️ How to Change Core Infrastructure](#7-️-how-to-change-core-infrastructure)
- [8. 🌍 Dynamic OAuth Configurations](#8--dynamic-oauth-configurations)
- [9. 🔐 Integrating Authorization](#9--integrating-authorization)
- [10. 📧 Email Templates & Developer Previews](#10--email-templates--developer-previews)
- [11. ⚙️ Background Task Processing (Celery)](#11-️-background-task-processing-celery)
- [12. 🚨 Production Deployment Checklist](#12--production-deployment-checklist)

---

## 1. 🏗️ Architecture Overview

The project is structured as a **Modular Monolith** using Domain-Driven Design (DDD) and Hexagonal Architecture. This ensures business logic remains pristine and uncoupled from infrastructure.

### 1.1 The Modules

```
src/
├── core/               # App-wide infrastructure: config, DB, container (DI root), Celery
├── shared/             # Reusable adapters & ports: logging, encryption, UoW, caching
├── api/                # Top-level FastAPI router that mounts all module routers
└── modules/
    ├── auth/ # Identity verification, OAuth, sessions, password flows, email OTP
    ├── users/          # User profile lifecycle (read, update, soft-delete)
    ├── projects/       # Multi-project isolation: API keys, OAuth config, CORS, environments
    ├── analytics/      # Multi-Tiered Rate Limiting and Usage Tracking events
    └── superadmin/     # Health, system logs, and platform-control endpoints for Global Admins
```

### 1.2 Inside Each Module (Hexagonal Layers)

Each module (except `core` and `shared`) is divided into distinct, decoupled layers:

| Layer | Path | Responsibility |
|---|---|---|
| **Domain** | `domain/` | Pure Python entities, value objects, domain exceptions. Zero framework imports. |
| **Application** | `application/` | Use cases and Port interfaces (`typing.Protocol`). Defines *what* the module does. |
| **Infrastructure** | `infrastructure/` | Concrete adapters: SQL repositories, OAuth clients, email sender. |
| **API** | `api/` | FastAPI routes + `dependencies.py` (FastAPI `Depends` wrappers that pull singletons from `AppContainer`). |

### 1.3 Dependency Injection (AppContainer)

All infrastructure singletons are instantiated **once** at startup in `src/core/container.py`:

```python
from src.core.container import app_container

# Access any singleton directly
app_container.user_repo
app_container.auth_usecase
app_container.cache_adapter
app_container.claims_provider
# ...
```

Module `dependencies.py` files are thin FastAPI wrappers that pull from `app_container` via `Depends()`. They do **not** instantiate anything themselves.

> To swap an infrastructure dependency, update the relevant line in `src/core/container.py`.

### 1.4 Transaction Management (Unit of Work)

This project enforces the **Unit of Work (UoW)** pattern to manage database transactions cleanly:
- Routes inject `SQLAlchemyUnitOfWork` and wrap use case execution in an `async with uow:` block.
- Repositories **never** call `commit()` directly; they only perform data manipulation and `flush()`.
- The UoW automatically commits on success, or rolls back on exception, ensuring atomicity.

---

## 2. 🏢 Project Management

### 2.1 Roles
- **Dashboard User**: The account that owns the Cerberus dashboard. Creates Projects, configures OAuth providers, and manages project settings.
- **End-User (Client User)**: The end-users logging into *your* applications. They are strictly scoped to a single Project.

### 2.2 Project Management & Environments
You can create multiple isolated **Projects**.
- Each project is assigned a unique API Key. External applications must pass this key via the `X-Cerberus-API-Key` header.
- **Environment Toggle:** Projects have an `environment` property (Development or Production).
  - **Development Mode:** Disables global rate-limits for the project's endpoints, allowing local testing without IP-blocking.
  - **Production Mode:** Enforces all strict security policies, limits, and caches.

### 2.3 Dynamic CORS Origins
Cerberus runs a background synchronization task (`ProjectConfigSyncTask`) that caches all project rules in memory.
- You can dynamically whitelist new frontend URLs (e.g., `https://my-app.com`) directly from the Cerberus Dashboard.
- Cerberus's `DynamicCORSMiddleware` evaluates these rules in real-time for every request.

---

## 3. 🚀 Getting Started

> **Note on Architecture:** Because Cerberus strictly follows Clean Architecture, the default tech stack (PostgreSQL, Redis, Resend, Celery) is completely decoupled from the core logic and is **100% swappable**.

### 3.1 Prerequisites
- **Python 3.12+** with [`uv`](https://docs.astral.sh/uv/) (or Docker)
- **Database**: PostgreSQL
- **Cache & Message Broker**: Redis

### 3.2 Setup Instructions

**Using Docker (Recommended)**
1. Copy the configuration from the root directory:
   ```bash
   cp .env.example .env
   # Edit .env with your Postgres, Redis, and email credentials
   ```
2. **Generate Security Keys & Credentials**:
   ```bash
   # Generate RSA keypair for JWT signing (saved to backend/keys/)
   uv run scripts/generate_keys.py

   # Generate a secure Redis ACL file
   uv run scripts/generate_redis_acl.py
   ```
   > Keys are loaded automatically from `backend/keys/` at startup — no path env vars needed.
3. Spin up the entire stack:
   ```bash
   docker compose pull
   docker compose up -d
   ```

**Local Python Setup (Using uv)**
1. Install dependencies:
   ```bash
   uv sync
   ```
2. Set up the environment:
   ```bash
   cp ../.env.example ../.env
   # Edit with your local credentials
   ```
3. Run database migrations:
   ```bash
   uv run alembic upgrade head
   ```
4. Start the FastAPI server:
   ```bash
   uv run fastapi dev src/main.py
   ```
5. In a new terminal, start the Celery worker:
   ```bash
   uv run celery -A src.core.celery_app worker --loglevel=info -P solo
   ```

---

## 4. ⚙️ Environment Variables Guide

All variables are loaded by Pydantic Settings classes in `src/core/config/`. The `.env.example` at the root is the canonical reference.

### 4.1 General & Security
| Variable | Description |
|---|---|
| `ENV` | `"development"` enables Swagger UI and dev routes. `"production"` enforces strict cookies and disables debug endpoints. |
| `FRONTEND_URL` | Used to build deep links (e.g. password reset URLs) sent in emails. |
| `CORS_ORIGINS` | Comma-separated list of allowed origins for the *Cerberus Dashboard* itself. |
| `SUPERADMIN_EMAIL` | Email of the Global Admin account bootstrapped on first run. |
| `SESSION_SECRET` | 32-byte hex secret used to sign CSRF state tokens. |
| `ENCRYPTION_KEY` | Fernet key (base64 URL-safe) used to encrypt project private keys at rest. |
| `ACCOUNT_RETENTION_DAYS` | Days to retain soft-deleted accounts before permanent deletion (default: `30`). |
| `LOG_RETENTION_DAYS` | Days to retain system logs before purging (default: `28`). |
| `RATE_LIMIT_ENABLED` | Global toggle for rate limiting (default: `true`). Independent of the `ENV` setting. |

> **JWT Keys:** RSA keys are loaded automatically from `backend/keys/jwt_private.pem` and `backend/keys/jwt_public.pem`. Generate them with `uv run scripts/generate_keys.py`.

### 4.2 Infrastructure
| Variable | Description |
|---|---|
| `PGSQL_URL` | PostgreSQL async connection string (`postgresql://...`). |
| `CACHE_URL` | Redis URL used for rate limiting, OTP storage, and JWT blacklisting (DB 0). |
| `CELERY_BROKER_URL` | Redis URL for Celery task dispatch (DB 1). |
| `CELERY_RESULT_URL` | Redis URL for Celery result storage (DB 2). |
| `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD` | Used by the `cerb-postgres` Docker container directly. |
| `REDIS_USER` / `REDIS_PASSWORD` | Used to generate the `redis.acl` file via `scripts/generate_redis_acl.py`. Not read by the application directly. |

### 4.3 Email Provider
| Variable | Description |
|---|---|
| `EMAIL_API_KEY` | Your [Resend](https://resend.com) API key. |
| `EMAIL_FROM` | The sender address shown to users. Must be verified with your provider. |
| `EMAIL_TEMPLATE_NAME` | Visual theme for outbound emails (`modern`, `minimal`, `elegant`). |

### 4.4 Token, Verification & Rate Limiting
| Variable | Description |
|---|---|
| `TOKEN_ACCESS_TOKEN_LIFETIME_MINUTES` | How long the stateless JWT is valid (default: `15`). |
| `TOKEN_REFRESH_TOKEN_LIFETIME_DAYS` | How long a user stays logged in (default: `7`). |
| `VERIFICATION_OTP_EXPIRATION_SECONDS` | How long a 6-digit OTP is valid after being issued (default: `300`). |
| `VERIFICATION_OTP_RESEND_WINDOW_SECONDS` | Window during which the same OTP attempt counter applies (default: `900`). |
| `VERIFICATION_OTP_MAX_ATTEMPTS` | Max failed OTP attempts before lockout (default: `5`). |
| `VERIFICATION_PASSWORD_RESET_EXPIRY_SECONDS` | How long a password reset token is valid (default: `900`). |
| `RATE_LIMIT_LOGIN_RATE_LIMIT` | Brute-force protection on login endpoints (default: `5/minute`). |
| `RATE_LIMIT_REFRESH_RATE_LIMIT` | Rate limit on the token refresh endpoint (default: `30/minute`). |
| `RATE_LIMIT_DEFAULT_RATE_LIMIT` | Default limit for all other endpoints (default: `60/minute`). |

> **Custom Multi-Tiered Rate Limiter:** Cerberus implements a highly performant, custom Redis-based Token Bucket rate limiter. It operates on two tiers:
> 1. **Tier 1 (IP Address)**: Protects the platform from aggressive bot brute-forcing.
> 2. **Tier 2 (API Key)**: Protects billing and resource limits for a specific tenant/project.
> Rate limits concurrently emit `API_REQUEST` usage events for analytics.

---

## 5. 🔄 Authentication Workflows

### 5.1 Local Registration
A database-first registration flow prevents malicious actors from claiming emails they don't own.
- A user is saved immediately with `is_verified=False`. They must verify their email using a 6-digit OTP within 5 minutes.
- **Brute-Force Protection:** The OTP flow implements atomic counting and locks after 5 failed attempts.
- **Garbage Collection:** A background task automatically purges unverified accounts older than 24 hours.

### 5.2 Login & Session Issuance (Local)
A dual-token system is utilized for security:
- **Refresh Token**: 32-byte hash saved in the DB, sent as an `HttpOnly` Secure cookie.
- **Access Token**: Short-lived (15m) RS256 JWT returned in the JSON payload from the `/refresh` endpoint.

### 5.3 Login & Session Issuance (OAuth)
The OAuth flow uses a secure exchange code pattern to prevent cross-subdomain cookie leakage:
1. Once the provider confirms identity, the backend stores the refresh token in Redis under a short-lived one-time exchange code (2 min TTL).
2. It redirects the browser to `<frontend_url>/auth/callback?code=<uuid>`.
3. The frontend calls `POST /auth/exchange` (or `POST /auth/tenant/exchange` for dashboard users) with the code to set the `HttpOnly` session cookies.

**Tenant OAuth vs Project OAuth:**
- **Tenant OAuth (`/auth/tenant/login/{provider}`):** Used by Dashboard Users. Uses the global `.env` fallback credentials (`GOOGLE_CLIENT_ID`, etc.) and does not require an API Key.
- **Project OAuth (`/auth/login/{provider}`):** Used by End-Users. Dynamically resolves credentials per-project from the project's configuration and requires the `X-Cerberus-API-Key`.

### 5.4 Session Rotation
To mitigate token theft, the system implements **lazy Refresh Token rotation**. Rather than rotating on every call, the token is only rotated when it has **≤ 30% of its lifetime remaining**. Most `/refresh` calls simply re-validate the existing token and issue a new Access Token without touching the Refresh Token.

### 5.5 Logout & Session Revocation
- **Access Token (`jti`) blacklist** — The current access token's unique ID is written to Redis with a TTL equal to its remaining lifetime. Subsequent requests with that token are immediately rejected.
- **Refresh Token soft-invalidation** — On logout, device revocation, password change, or password reset, all refresh tokens in the session family are marked `used=True` in the database.

### 5.6 Security Alerts & Anomaly Detection
Cerberus actively monitors session fingerprints:
- **New Login Detection**: If a login originates from an unrecognized IP or User-Agent, a security alert email is dispatched immediately.
- **Account Recovery Alerts**: If a user restores a soft-deleted account by logging in, they receive a notification email to confirm the action was intentional.

---

## 6. 💻 Frontend Integration Guidelines

> **🚨 SKIP THE BOILERPLATE:** The easiest way to integrate Cerberus is the official **[TypeScript SDK](https://github.com/Avneesh11905/cerberus-sdk)**. It handles token rotation, interceptors, and CSRF protection automatically.

### 6.1 Required Frontend Routes
- 🏠 **`/`**: Handle post-login redirects and email verification success states.
- 🔑 **`/reset-password`**: Where users land from the "Reset Password" email link. Read the `token` from the URL and `POST` to `/auth/password/reset`.
- 🔄 **`/auth/callback`**: OAuth landing page. Reads `?code=` and calls `POST /auth/exchange` to complete session setup.

### 6.2 API Reference Checklist
> **Interactive Docs:** Run the backend and visit **`http://localhost:8000/docs`** for the Swagger UI.

**Core Auth Endpoints:**
- `POST /auth/register` (Requires `X-Cerberus-API-Key`)
- `POST /auth/verify-email`
- `POST /auth/login/local`
- `POST /auth/oauth/preflight/{provider}`
- `GET /auth/login/{provider}` (OAuth callback from provider for project users)
- `GET /auth/tenant/login/{provider}` (OAuth callback from provider for tenant/dashboard users)
- `POST /auth/exchange` (Converts a one-time OAuth code into HttpOnly session cookies)
- `POST /auth/refresh` (Rotates HttpOnly cookie and issues new JWT)
- `POST /auth/logout`
- `POST /auth/logout/all`
- `GET /auth/sessions` (List active sessions)
- `DELETE /auth/sessions/{family_id}` (Revoke a specific device session)

### 6.3 Handling Token Rotation (Axios Example)
Use an HTTP interceptor to silently catch `401` responses, call `/auth/refresh`, and retry the original request.

```javascript
axios.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;
            try {
                const { data } = await axios.post('/auth/refresh');
                axios.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`;
                originalRequest.headers['Authorization'] = `Bearer ${data.access_token}`;
                return axios(originalRequest);
            } catch (refreshError) {
                window.location.href = '/login';
            }
        }
        return Promise.reject(error);
    }
);
```

### 6.4 CSRF Protection Details
State-changing operations on sensitive endpoints require an `X-CSRF` header.
After `POST /auth/exchange` or `POST /auth/refresh`, the backend returns `csrf_token` in the JSON body. Store this in memory and attach it as the `X-CSRF` header on all subsequent mutation requests. The official SDK handles this automatically.

---

## 7. 🛠️ How to Change Core Infrastructure

Because the Core business logic only communicates through **Ports**, you can replace any infrastructure piece by writing a new **Adapter** and wiring it in `src/core/container.py`.

### The Universal Swap Pattern
1. **Find the Port** — Locate the `typing.Protocol` interface in `src/modules/<module>/application/ports/`.
2. **Write a new Adapter** — Create a new file in `src/modules/<module>/infrastructure/` and implement every method on the Port.
3. **Plug it in** — Open `src/core/container.py` and swap the instantiation on the relevant `app_container` attribute.

### Examples

**Swapping the Cache (e.g. Redis → Memcached)**
The backend ships with `RedisCacheAdapter`. Write an adapter implementing `CachePort` and update `app_container.cache_adapter` in `src/core/container.py`.

**Swapping the Email Provider (e.g. Resend → SendGrid)**
1. Create `src/modules/auth/infrastructure/sendgrid_email_client.py`.
2. Implement `EmailSenderPort`.
3. Update `app_container.auth_email_sender` in `src/core/container.py`.

**Swapping the Database**
1. Create a new repository adapter, e.g. `src/modules/auth/infrastructure/repository/mongo_user_repository.py`, implementing `UserRepositoryPort`.
2. Update `app_container.user_repo` in `src/core/container.py`.

---

## 8. 🌍 Dynamic OAuth Configurations

Unlike traditional backends that hardcode OAuth credentials in `.env`, **Cerberus allows you to configure different credentials per project**.

- Navigate to the Project Dashboard and set the `client_id` and `client_secret` for Google or GitHub.
- When an end-user hits `/auth/oauth/preflight/google` (passing the `X-Cerberus-API-Key`), the backend dynamically injects the project's specific credentials into Authlib.
- Global fallback credentials from `.env` (`GOOGLE_CLIENT_ID`, etc.) are used only if the project has no credentials configured.

---

## 9. 🔐 Integrating Authorization

Cerberus handles **Authentication** (identity verification) and leaves **Authorization** (access control) open for your implementation.

Bridge your logic by implementing the `ClaimsProviderPort` located at `src/modules/authorization/`. This governs:
- What custom claims (roles, permissions) get injected into the JWT upon issue.
- Stateful database-level permission checks for endpoints using `require_permission(action, resource)`.

Use `require_role("admin")` or `require_permission("read", "reports")` from `src/modules/authorization/api/dependencies.py` directly in your route `Depends()` list.

---

## 10. 📧 Email Templates & Developer Previews

Cerberus uses beautifully styled Jinja2 HTML templates for all outbound emails (OTP codes, password resets, welcome emails, security alerts). Templates are located in `src/shared/templates/emails/`.

If `ENV="development"` is set, navigate to **`http://localhost:8000/dev/email/preview`** to preview all templates side-by-side, toggle themes (`modern`, `minimal`, `elegant`), and toggle Dark Mode.

---

## 11. ⚙️ Background Task Processing (Celery)

FastAPI is incredibly fast, but sending emails or running cleanup jobs can block the event loop. Cerberus uses a **Celery** pipeline backed by Redis to ensure APIs return instantly.

Tasks are defined in `src/modules/auth/infrastructure/tasks.py` and dispatched via the `app_container.task_runner`. Example:

```python
from src.core.container import app_container

app_container.task_runner.add_task("src.modules.auth.infrastructure.tasks.dispatch_email_task", email, subject, html)
```

**Worker Lifecycle:**
In production (`docker-compose.yml`), there are two Celery containers:
- `cerb-celery-worker`: Processes all background tasks (emails, cleanups). Scales horizontally.
- `cerb-celery-beat`: Celery Beat scheduler for recurring tasks (purging expired tokens, old logs).

---

## 12. 🚨 Production Deployment Checklist

Before deploying Cerberus to a live environment, verify the following:

- [ ] **Set Environment to Production:** `ENV="production"` enforces secure cookies and disables debug endpoints.
- [ ] **Strictly Define CORS Origins:** Set `CORS_ORIGINS` to your exact frontend domain(s).
- [ ] **Generate RSA Keys:** Run `uv run scripts/generate_keys.py` and ensure `backend/keys/` is mounted into containers.
- [ ] **Secure Redis:** Run `uv run scripts/generate_redis_acl.py` and ensure the ACL file is mounted into `cerb-redis`.
- [ ] **Run the Celery Worker & Beat Scheduler:** Ensure `cerb-celery-worker` and `cerb-celery-beat` are running.
- [ ] **Understand Cookie Boundaries (`SameSite`):** Cerberus uses `SameSite=None; Secure` cookies. The frontend and backend can be on completely separate domains — just ensure HTTPS is used on both ends.
- [ ] **Cloudflare Tunnel / Proxy:** If deployed behind Cloudflare, ensure `ProxyHeadersMiddleware` uses `trusted_hosts="*"` so `X-Forwarded-Proto` is read correctly. Ensure `get_client_ip()` reads `CF-Connecting-IP` to prevent rate-limit bypass via IP spoofing.
- [ ] **Switch Projects to Production Mode:** Toggle all projects to `environment=production` before go-live. Development mode disables rate limiting globally for that project's endpoints.
