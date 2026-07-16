# 🏢 Projects Domain

The `projects` domain manages the multi-tenant architecture of Cerberus. It handles the creation of Projects, API Keys, environment toggling, and dynamic CORS origins.

## 🏗️ Architecture
- **API (`api/`)**: Endpoints for creating projects, rotating API keys, updating environments (Dev/Prod), and configuring OAuth credentials.
- **Core (`core/`)**: Business logic enforcing tenant isolation. Ensures that a user can only access or modify projects they own.
- **Adapters (`adapters/`)**: Interacts with the `projects`, `project_api_keys`, and `project_oauth_configs` database tables.

## 🌍 Multi-Tenancy & Environments
- **Environments**: Projects can be toggled between `development` and `production` modes. Development mode bypasses strict rate-limiting for easier local testing.
- **API Keys**: Each project is assigned a unique API key, which must be passed in the `X-Cerberus-API-Key` header for public integrations.
- **CORS Synchronization**: The domain triggers cache updates whenever a tenant modifies their allowed CORS origins, instantly updating the global middleware.
