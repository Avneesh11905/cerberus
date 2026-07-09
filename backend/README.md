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
- **Distributed Background Processing:** Production-ready background tasks using Celery and Redis to handle email dispatches and logging asynchronously.

> **Infrastructure Independence:** Out of the box, this platform is **SQL-based** (using SQLAlchemy & Alembic), but because the system is deeply modular, you are not locked in! You can easily swap out the SQL database, cache, or email provider by writing a new adapter.

---

## 📑 Table of Contents
- [📖 Introduction](#-introduction)
- [1. 🏗️ Architecture Overview](#1-️-architecture-overview)
  - [1.1 The Domains](#11-the-domains)
  - [1.2 Inside Each Domain (Hexagonal Layers)](#12-inside-each-domain-hexagonal-layers)
  - [1.3 Transaction Management (Unit of Work)](#13-transaction-management-unit-of-work)
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
- [6. 💻 Frontend Integration Guidelines](#6--frontend-integration-guidelines)
  - [6.1 📍 Required Frontend Routes](#61--required-frontend-routes)
  - [6.2 🗺️ API Reference Checklist](#62-️-api-reference-checklist)
  - [6.3 ♻️ Handling Token Rotation (Axios Example)](#63-️-handling-token-rotation-axios-example)
  - [6.4 🛡️ CSRF Protection Details](#64-️-csrf-protection-details)
- [7. 🛠️ How to Change Core Infrastructure](#7-️-how-to-change-core-infrastructure)
- [8. 🌍 Dynamic OAuth Configurations](#8--dynamic-oauth-configurations)
- [9. 🔐 Integrating Authorization](#9--integrating-authorization)
- [10. 📧 Email Templates & Developer Previews](#10--email-templates--developer-previews)
- [11. ⚙️ Background Task Processing (Celery)](#11-️-background-task-processing-celery)
- [12. 🚨 Production Deployment Checklist](#12--production-deployment-checklist)

---

## 1. 🏗️ Architecture Overview

The project is structured into modular domains using Domain-Driven Design (DDD) and Hexagonal Architecture. This ensures business logic remains pristine and uncoupled from infrastructure.

### 1.1 The Domains
1. **`src/shared/`**: The backbone of the application. Contains database connections, caching clients (Redis), the Celery task runner, application lifecycle events, and global exception handlers.
2. **`src/authentication/`**: Handles identity verification. Manages local registration, dynamic OAuth integrations, password resets, email verification, and issues JWTs. 
3. **`src/users/`**: Manages the user profile lifecycle (fetching profiles, updating display names, deleting accounts) independently from the authentication logic.
4. **`src/projects/`**: Manages the core multi-project isolation logic. You can create Projects, configure API keys, update OAuth credentials, add CORS allowed origins, and toggle environment modes.
5. **`src/authorization/`**: Contains the business rules for access control (RBAC/PBAC) and injects permissions into your JWTs.
6. **`src/admin/`**: Provides health monitoring, system logs, and platform control endpoints exclusive to Global Admins.

### 1.2 Inside Each Domain (Hexagonal Layers)
Each domain (except `shared`) is divided into distinct, decoupled layers:
- **Core (`core/`)**: Contains pure Python business rules and Use Cases. It has zero knowledge of FastAPI, SQLAlchemy, or external APIs.
- **Ports (`core/ports/`)**: Abstract interfaces (`typing.Protocol`) that define external dependencies required by the Core (e.g., `CachePort`, `EmailSenderPort`).
- **Adapters (`adapters/`)**: Concrete implementations of the Ports (e.g., `RedisCacheAdapter`, `SQLUserRepositoryAdapter`, `CeleryTaskRunner`).
- **API (`api/`)**: FastAPI routes acting as the entry point. They translate HTTP requests into Python objects, execute Use Cases, and return HTTP responses.

### 1.3 Transaction Management (Unit of Work)
This project enforces the **Unit of Work (UoW)** pattern to manage database transactions cleanly:
- Routes inject the `SQLAlchemyUnitOfWork` and wrap use case execution in an `async with uow:` block.
- Repositories **never** call `commit()` directly; they only perform data manipulation and `flush()`.
- The UoW automatically commits the transaction at the end of the block if successful, or rolls back if an exception occurs, ensuring atomicity across multiple repository operations.

---

## 2. 🏢 Project Management

### 2.1 Roles
- **Dashboard User**: The account that owns the Cerberus dashboard. Creates Projects, configures OAuth providers, and manages project settings.
- **End-User (Client User)**: The end-users logging into *your* applications. They are strictly scoped to a single Project.

### 2.2 Project Management & Environments
You can create multiple isolated **Projects**. 
- Each project is assigned a unique API Key. External applications must pass this key via the `X-Cerberus-API-Key` header.
- **Environment Toggle:** Projects have an `environment` property (Development or Production). 
  - **Development Mode:** Cerberus disables global rate-limits for the project's endpoints, allowing you to test applications locally without getting IP-blocked.
  - **Production Mode:** Enforces all strict security policies, limits, and caches.

### 2.3 Dynamic CORS Origins
Cerberus runs a background synchronization task (`ProjectConfigSyncTask`) that caches all project rules in memory.
- You can dynamically whitelist new frontend URLs (e.g., `https://my-app.com`) directly from the Cerberus Dashboard.
- Cerberus's `DynamicCORSMiddleware` evaluates these rules in real-time, allowing isolated and secure cross-origin requests for every project instantly.

---

## 3. 🚀 Getting Started

> **Note on Architecture:** Because Cerberus strictly follows Clean Architecture, the default tech stack (PostgreSQL, Redis, Resend, Celery) is completely decoupled from the core logic and is **100% swappable**.

### 3.1 Prerequisites
- **Python 3.12+** (Or Docker)
- **Database**: PostgreSQL
- **Cache & Message Broker**: Redis

### 3.2 Setup Instructions

**Using Docker (Recommended)**
1. Copy the configuration from the root directory:
   ```bash
   cp .env.example .env
   ```
2. **Generate Security Keys & Credentials**:
   Ensure you generate a secure RSA keypair for JWT signing by running `uv run scripts/generate_keys.py`. The keys will be saved as `.pem` files in the `backend/keys/` directory, which the Docker containers will automatically mount and read.
   Additionally, you must secure your Redis instance by generating an ACL file with `uv run scripts/generate_redis_acl.py`.
3. Spin up the entire stack (API, Celery Worker, PostgreSQL, Redis) with a single command:
   ```bash
   docker compose pull
   docker compose up -d
   ```

**Local Python Setup (Using uv)**
1. Ensure you have [`uv`](https://docs.astral.sh/uv/) installed.
2. Clone the repository and install dependencies:
   ```bash
   uv sync
   ```
3. Set up the environment variables (you can use the `.env.example` in the root folder):
   ```bash
   cp .env.example .env
   ```
4. Run database migrations:
   ```bash
   uv run alembic upgrade head
   ```
5. Start the FastAPI server:
   ```bash
   uv run fastapi dev main.py
   ```
6. In a new terminal, start the Celery worker for background jobs:
   ```bash
   uv run celery -A src.shared.adapters.task_runner.celery_app worker --loglevel=info -P solo
   ```

---

## 4. ⚙️ Environment Variables Guide

The `.env` and `docker-compose.yml` files control the entire behavior of the application and are organized into 6 logical blocks (Application & Server, Databases & Cache, Security & Authentication, OAuth Providers, Email Configuration, and Rate Limiting). Here are some core variables:

### 4.1 General & Security
| Variable | Description |
|---|---|
| `FRONTEND_URL` | Used to build deep links (like password reset URLs) sent in emails. |
| `ENV` | `"development"` enables development routes and swagger UI. `"production"` enforces strict cross-origin policies and disables debug endpoints. |
| `CORS_ORIGINS` | Comma-separated list of allowed frontend URLs for the *Cerberus Dashboard itself*. |
| `SESSION_SECRET` | Used to cryptographically sign the `X-CSRF` state validation. |
| `JWT_PRIVATE_KEY_PATH` / `JWT_PUBLIC_KEY_PATH` | Path to the RSA `.pem` keys used to *sign* and *verify* Access Tokens. |
| `ACCOUNT_RETENTION_DAYS` | Number of days to retain soft-deleted user accounts before permanent deletion (e.g. `30`). |

### 4.2 Infrastructure
| Variable | Description |
|---|---|
| `DB_ASYNC_URL` | Connection string to your PostgreSQL database. |
| `CACHE_URL` | Redis instance used for Rate Limiting and JWT Blacklisting. |
| `CELERY_BROKER_URL` | Redis URL for Celery to dispatch tasks. |
| `CELERY_RESULT_BACKEND` | Redis URL for Celery to store task results. |

### 4.3 Email Provider
| Variable | Description |
|---|---|
| `EMAIL_API_KEY` | Your Resend API key. |
| `EMAIL_FROM` | The email address shown to users. Must be verified with your provider. |
| `EMAIL_TEMPLATE_NAME` | Select the visual theme for all outbound emails (`modern`, `minimal`, `elegant`). |

### 4.4 Token, Verification & Rate Limiting
| Variable | Description |
|---|---|
| `TOKEN_ACCESS_TOKEN_LIFETIME_MINUTES` | How long the stateless JWT is valid (e.g. `15`). |
| `TOKEN_REFRESH_TOKEN_LIFETIME_DAYS` | How long a user stays logged in (e.g. `7`). |
| `VERIFICATION_OTP_EXPIRATION_SECONDS` | How long a 6-digit OTP is valid after being issued (e.g. `300`). |
| `RATE_LIMIT_LOGIN_RATE_LIMIT` | Strict slow-down on the login endpoints to prevent brute forcing (`5/minute`). |

---

## 5. 🔄 Authentication Workflows

### 5.1 Local Registration
A database-first registration flow prevents malicious actors from claiming emails they don't own. 
- A user is saved immediately with `is_verified=False`. They must verify their email using a 6-digit OTP within 5 minutes.
- **Brute-Force Protection:** The OTP flow implements atomic counting and strictly locks the account registration process after 5 failed attempts.
- **Garbage Collection:** A background task automatically purges unverified user accounts older than 24 hours.

### 5.2 Login & Session Issuance (Local)
A dual-token system is utilized for security:
- **Refresh Token**: 32-byte hash saved in the DB, sent to the client as an `HttpOnly` Secure cookie.
- **Access Token**: Short-lived (15m) RS256 JWT returned in the JSON payload from the `/refresh` endpoint.

### 5.3 Login & Session Issuance (OAuth)
The OAuth flow utilizes a secure exchange code pattern to prevent cross-subdomain cookie leakage:
1. Once the provider confirms identity, the backend stores the refresh token in Redis under a short-lived one-time exchange code (2 min TTL).
2. It redirects the browser back to the frontend at `<frontend_url>/auth/callback?code=<uuid>`.
3. The frontend calls `POST /auth/exchange` with the code to set the `HttpOnly` session cookies.
*Note: In Cerberus, this dynamically uses the OAuth Configuration defined for the specific project.*

### 5.4 Session Rotation
To mitigate token theft, the system implements **lazy Refresh Token rotation**. Rather than rotating the token on every single call (which causes unnecessary DB writes), the token is only rotated when it has **≤ 30% of its lifetime remaining**. Most `/refresh` calls simply re-validate the existing token and issue a new Access Token without touching the Refresh Token at all.

### 5.5 Logout & Session Revocation
- **Access Token (`jti`) blacklist** — Because JWTs are stateless, the current access token's unique ID (`jti`) is written to the Redis cache with a TTL equal to its remaining lifetime. Any subsequent request bearing that token is rejected immediately.
- **Refresh Token soft-invalidation** — On logout, device revocation (`DELETE /auth/sessions/{family_id}`), **password changes**, or **password resets**, all refresh tokens in the session family are marked `used=True` in the database.

### 5.6 Security Alerts & Anomaly Detection
Cerberus actively monitors session fingerprints to protect end-users:
- **New Login Detection**: When a user logs in, their IP Address and User-Agent are evaluated against their currently active sessions. If the device or location is unrecognized, an immediate security alert email is dispatched. (This is suppressed on the very first login after verification to avoid spam).
- **Account Recovery Alerts**: If a user restores a soft-deleted account by logging in, they receive an immediate notification email to confirm the action was intentional.

---

## 6. 💻 Frontend Integration Guidelines

> **🚨 SKIP THE BOILERPLATE:** The absolute easiest way to integrate Cerberus into your frontend is by using the official, strictly-typed **[TypeScript SDK](https://github.com/Avneesh11905/cerberus-sdk)**. It handles token rotation, interceptors, and CSRF protection automatically!

If you prefer to build the client yourself, building the frontend to integrate with Cerberus involves using the `X-Cerberus-API-Key` on requests, handling JWTs, and passing CSRF tokens.

### 6.1 📍 Required Frontend Routes
- 🏠 **`/` (The Root Route)**: Make sure your root route can handle post-login redirects and email verification success states.
- 🔑 **`/reset-password`**: This is where users land when they click the "Reset Password" link in their email. Parse the `token` from the URL, show a form, and `POST` it to `/auth/password/reset`.
- 🔄 **`/auth/callback`**: The landing page for OAuth logins. It reads the `?code=` query parameter and calls `POST /auth/exchange` to complete the session setup.

### 6.2 🗺️ API Reference Checklist
> **Interactive Documentation:** Run the backend and visit **`http://localhost:8000/docs`** for the auto-generated Swagger UI.

**Core Auth Endpoints:**
- `POST /auth/register` (Requires API Key)
- `POST /auth/verify-email`
- `POST /auth/login/local`
- `POST /auth/oauth/preflight/{provider}` (Generates state and OAuth redirect URL)
- `GET /auth/login/{provider}` (OAuth Callback from provider)
- `POST /auth/exchange` (Converts a one-time OAuth exchange code into HttpOnly session cookies. No CSRF required)
- `POST /auth/refresh` (Rotates HttpOnly cookie and issues JWT)
- `POST /auth/logout`
- `POST /auth/logout/all` (Revokes all sessions for the user)

### 6.3 ♻️ Handling Token Rotation (Axios Example)
Use an HTTP interceptor to automatically catch `401 Unauthorized` responses, silently call the `/auth/refresh` endpoint to get a new Access Token, and retry their pending request transparently.

```javascript
axios.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;
        
        // If it's a 401 and we haven't already retried this exact request...
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;
            try {
                // Silently request a new token using the HttpOnly Refresh Token cookie!
                const { data } = await axios.post('/auth/refresh');
                
                axios.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`;
                originalRequest.headers['Authorization'] = `Bearer ${data.access_token}`;
                return axios(originalRequest);
                
            } catch (refreshError) {
                // If the refresh fails, their session is dead. Boot them to login.
                window.location.href = '/login';
            }
        }
        return Promise.reject(error);
    }
);
```

### 6.4 🛡️ CSRF Protection Details
State-changing operations on sensitive endpoints require an `X-CSRF` header.
Because cookies are strictly host-only (set on `cerberus-api`), cross-origin frontend apps cannot read the `csrf_token` via `document.cookie`. 

Instead, after a successful OAuth exchange via `POST /auth/exchange` or a session refresh via `POST /auth/refresh`, the backend returns the `csrf_token` inside the JSON response body. 
Your frontend must store this token in memory and attach it as the `X-CSRF` header on all subsequent requests. The official Cerberus SDK handles this automatically via the `cerberus.auth.handleOAuthCallback()` helper method and silent refreshes.

---

## 7. 🛠️ How to Change Core Infrastructure

Because the Core business logic only communicates through **Ports**, you can completely replace any infrastructure by simply writing a new **Adapter**.

### 7.1 Swapping the Cache
The backend ships with `RedisCacheAdapter`. To plug in Memcached, write an adapter implementing `CachePort` and plug it into the `shared_container`.

### 7.2 Swapping the Email Provider
Currently, the template uses `ResendEmailClient`. To swap it to SendGrid:
1. Create a new file: `src/shared/adapters/sendgrid_email_client.py`.
2. Implement the `SharedEmailClientPort` protocol.
3. Update the Composition Root to use your new adapter.

### 7.3 How to Change the Database
1. Create a new adapter `src/authentication/adapters/mongo_user_repository.py` that implements `UserRepositoryPort`.
2. Plug it into `src/authentication/api/container.py`.

### 7.4 The Universal Swap Pattern
1. **Find the Port** — Locate the `typing.Protocol` interface in `src/<domain>/core/ports/`.
2. **Write a new Adapter** — Create a new file in `src/<domain>/adapters/` and implement every method.
3. **Plug it in** — Open `src/<domain>/api/container.py` and swap out the old adapter.

---

## 8. 🌍 Dynamic OAuth Configurations

Unlike traditional backends that hardcode Google/GitHub credentials in the `.env` file, **Cerberus allows you to configure different credentials per project!**

- Navigate to the Project Dashboard and input the `client_id` and `client_secret` for Google or GitHub.
- When an end-user hits the `/auth/oauth/preflight/google` endpoint (passing the `X-Cerberus-API-Key` header), the backend dynamically injects the project's specific credentials into Authlib.

---

## 9. 🔐 Integrating Authorization

This template natively handles **Authentication** (identity verification) but leaves **Authorization** (access control) open so you can implement Role-Based Access Control (RBAC) or Policy-Based Access Control (PBAC).

You bridge your logic by implementing the `AuthorizationPort` located in `src/authorization/adapters/custom_authorization.py`, which governs what custom claims (roles) get injected into the JWT upon issue, and handles stateful database-level checks for endpoints.

---

## 10. 📧 Email Templates & Developer Previews

This template uses beautifully styled Jinja2 HTML templates for all outbound emails (verification codes, password resets, welcome emails, etc.). These templates are located in `src/shared/templates/emails/`.

If `ENV="development"` is set in your `.env`, navigate to **`http://localhost:8000/dev/email/preview`** to preview all templates side-by-side, toggle themes (`Modern`, `Minimal`, `Playful`), and toggle `Dark Mode`.

---

## 11. ⚙️ Background Task Processing (Celery)

FastAPI is incredibly fast, but sending emails or writing logs can block the event loop. Cerberus uses a **Celery** background task pipeline backed by Redis to ensure APIs return instantly.

The `CeleryTaskRunner` (located in `src/shared/adapters/task_runner/celery_task_runner.py`) dispatches tasks to the queue:

```python
from src.shared.container import shared_container

# Push it to the background and return immediately
shared_container.task_runner.add_task("src.authentication.infrastructure.tasks.send_welcome_email", user.email)
```

**Worker Lifecycle:**
In production (and `docker-compose.yml`), there are three Celery containers:
- `cerb-celery-worker`: Standard worker for processing emails and other background tasks.
- `cerb-celery-logs-worker`: Specialized worker bound to the `logs` queue using `celery-batches` for high-throughput DB log insertion.
- `cerb-celery-beat`: Celery Beat scheduler for recurring tasks (like purging expired tokens and old system logs).

---

## 12. 🚨 Production Deployment Checklist

Before deploying Cerberus to a live environment, you **must** verify the following:

- [ ] **Set Environment to Production:** Ensure `ENV="production"` is set to enforce secure cookies and disable debug endpoints.
- [ ] **Strictly Define CORS Origins:** Ensure `CORS_ORIGINS` is explicitly defined in your `.env`.
- [ ] **Run the Celery Workers & Beat Scheduler:** Ensure the background task workers and beat scheduler are running alongside your FastAPI instance.
- [ ] **Understand Cookie Boundaries (`SameSite`):** Because Cerberus uses `SameSite=None; Secure` cookies and the exchange code pattern, the frontend and backend can be on completely separate domains. No shared root domain or reverse proxy is required. Just ensure HTTPS is used on both ends.
- [ ] **Cloudflare Tunnel & Proxy Configuration:** If deployed via `cloudflared` (especially through a Docker bridge), ensure `ProxyHeadersMiddleware` uses `trusted_hosts="*"` so `X-Forwarded-Proto` is read correctly for `https` redirects. Additionally, ensure `get_client_ip()` in `src/shared/api/dependencies.py` reads `CF-Connecting-IP` (set by Cloudflare) instead of `X-Forwarded-For` to prevent rate-limit bypass via IP spoofing.
- [ ] **Switch projects to Production mode:** Ensure all projects are toggled to `environment=production` before go-live. Development mode disables rate limiting globally for that project's endpoints.
