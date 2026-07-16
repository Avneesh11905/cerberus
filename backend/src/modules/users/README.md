# 👤 Users Domain

The `users` domain is responsible for managing the lifecycle of the user profile, distinctly separated from the authentication logic.

## 🏗️ Architecture
- **API (`api/`)**: Endpoints for fetching the current profile (`GET /users/me`), updating display names, and account deletion.
- **Core (`core/`)**: Use cases enforcing profile modification rules and cascading deletion logic.
- **Adapters (`adapters/`)**: Database repositories for updating the `users` table.

## 🔄 Separation of Concerns
While the `authentication` domain handles *how* a user logs in (passwords, OAuth, OTPs), the `users` domain focuses purely on *who* the user is (name, avatar, preferences) and their relationship to the tenant project.
