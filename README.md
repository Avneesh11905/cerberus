<div align="center">
  <h1>🛡️ Cerberus Identity Platform</h1>
  <p>A professional, multi-tenant Auth-as-a-Service monorepo.</p>
</div>

---

## 📖 Overview

**Cerberus** is a complete, scalable, and strictly typed multi-tenant identity platform. This repository contains the core backend services and the global administration dashboard. 

It is designed to give business owners (Tenants) the ability to spin up isolated **Projects**, configure dynamic OAuth providers, manage environments (Development/Production), and securely manage end-users without locking into a single infrastructure stack.


## 📦 Repository Structure

This repository is divided into two primary services:

### 1. [`/backend`](./backend)
The core Auth-as-a-Service engine built with **FastAPI**. 
- Built with Domain-Driven Design (DDD) and Hexagonal Architecture.
- Handles dual-token session management (HttpOnly Refresh Cookies + JWT Access Tokens).
- Provides dynamic OAuth injection, RBAC, and Celery-based background task processing.
- Uses PostgreSQL (asyncpg) and Redis.
- [Read the Backend Documentation](./backend/README.md)

### 2. [`/frontend`](./frontend)
The **Cerberus Dashboard**, built with **TanStack Start**, Tailwind CSS, and Shadcn UI.
- The command center for Global Admins and Tenants.
- Manage Projects, API Keys, CORS rules, and environment toggles.
- Features Server-Side Rendering (SSR) and seamless secure API integration.
- [Read the Frontend Documentation](./frontend/README.md)

*(Note: The `/demo-app` directory contains an internal playground and is intentionally excluded from version control).*

---

## 🚀 Quick Start (Docker)

The fastest way to spin up the entire stack locally is by using Docker Compose.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Avneesh11905/cerberus.git
   cd cerberus
   ```

2. **Configure Environments:**
   - Copy `.env.example` to `.env` in the `backend/` directory and generate your RSA keys.
   - Copy `docker-compose.example.yml` to `docker-compose.yml` in the root directory.
   - Review your credentials and ensure ports aren't conflicting.

3. **Spin up the stack:**
   ```bash
   docker compose up --build
   ```

4. **Access the platform:**
   - **Backend API & Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
   - **Cerberus Dashboard:** [http://localhost:3000](http://localhost:3000)

## 🏗️ Deployment

The frontend and backend both include optimized multi-stage `Dockerfile`s ready for production. 
- Ensure `docker-compose.yml` and `.env` files are ignored in your production git tree.
- Mount your database and cache volumes correctly.
- Ensure the Cerberus Celery Worker (`celery_worker` in `docker-compose.yml`) is running to handle background emails and cleanup tasks.

## 📄 License
MIT License
