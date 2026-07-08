# 🛑 Authorization Domain

The `authorization` domain is responsible for Access Control (RBAC/PBAC). It determines *what* an authenticated user is allowed to do.

## 🏗️ Architecture
- **API (`api/`)**: Provides middleware and dependencies (e.g., `require_permissions`) to guard FastAPI endpoints.
- **Core (`core/`)**: Defines Roles, Permissions, and the policy evaluation engine.
- **Adapters (`adapters/`)**: Fetches user roles from the database or cache.

## 🔑 Key Concepts
- **Roles**: Logical groupings of permissions (e.g., `Admin`, `Member`, `Viewer`).
- **Permissions**: Granular actions (e.g., `project:read`, `user:delete`).
- **Hierarchical Access**: Permissions are evaluated strictly within the context of the user's `project_id`.
