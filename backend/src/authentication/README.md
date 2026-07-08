# 🔑 Authentication Domain

The `authentication` domain handles identity verification, session management, and OAuth integrations. It is the gatekeeper of the Cerberus platform.

## 🏗️ Architecture
- **API (`api/`)**: FastAPI routes for local login, registration, OAuth callbacks, token refresh, and logout. Includes CSRF protection middleware.
- **Core (`core/`)**: Houses the Use Cases for issuing JWTs, handling password resets, managing session families, and verifying OTPs.
- **Adapters (`adapters/`)**: Implements password hashing (Argon2), JWT signing (RS256), database repositories (`SQLUserRepositoryAdapter`), and Redis caching for session blacklists.

## 🔄 Core Workflows
1. **Local Registration**: Generates an OTP, sends an email via Celery, and waits for verification before creating a password hash.
2. **Session Issuance**: Returns a short-lived `access_token` in the JSON response and a long-lived `refresh_token` in an HttpOnly cookie.
3. **Session Rotation**: The `/refresh` endpoint issues a new `access_token` and rotates the `refresh_token` to prevent token theft.
