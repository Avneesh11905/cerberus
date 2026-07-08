<div align="center">

<img src="https://cerberus.aymahajan.in/logo.webp" alt="Cerberus Logo" width="80" />

# Cerberus Identity Platform

**A professional Auth-as-a-Service platform. Self-hosted, strictly typed, and production-ready.**

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![License](https://img.shields.io/badge/License-Proprietary-red?style=flat-square)](./LICENSE)

[🌐 Live Platform](https://cerberus.aymahajan.in) · [📖 SDK Docs](https://cerberus.aymahajan.in/docs/sdk) · [📦 TypeScript SDK](https://github.com/Avneesh11905/cerberus-sdk)

</div>

---

## 📖 Overview

**Cerberus** is a complete, scalable identity platform that gives you full control over your authentication infrastructure. This repository contains the core backend engine and the management dashboard.

It is designed to let you spin up isolated **Projects**, configure dynamic OAuth providers, manage environments (Development / Production), and securely manage end-users — without locking into any third-party identity provider.

> The official TypeScript SDK for integrating Cerberus into your frontend is available at **[Avneesh11905/cerberus-sdk](https://github.com/Avneesh11905/cerberus-sdk)**.

---

## 📦 Repository Structure

### [`/backend`](./backend)
The core Auth-as-a-Service engine built with **FastAPI**.
- Domain-Driven Design (DDD) and Hexagonal Architecture.
- Dual-token session management (HttpOnly Refresh Cookies + JWT Access Tokens).
- Dynamic OAuth injection, RBAC, and background task processing.
- PostgreSQL (asyncpg) + Redis.
- [Read the Backend Documentation →](./backend/README.md)

### [`/frontend`](./frontend)
The **Cerberus Dashboard**, built with **Vite + TanStack Router**, Tailwind CSS, and Shadcn UI.
- Manage Projects, API Keys, CORS rules, and environment toggles.
- Secure authentication integrated directly with the Cerberus API.
- [Read the Frontend Documentation →](./frontend/README.md)

---

## 🚀 Quick Start (Docker)

```bash
# 1. Clone
git clone https://github.com/Avneesh11905/cerberus.git
cd cerberus

# 2. Configure
cp example.env .env
# Edit .env with your Postgres, Redis, and email credentials
# Generate RSA keys (they will be saved to backend/keys/):
cd backend && uv run scripts/generate_keys.py && cd ..

# 3. Run
docker compose pull
docker compose up -d
```

**Access:**
- **API + Swagger Docs:** http://localhost:8000/docs
- **Dashboard:** http://localhost:3000

---

## 🏗️ Deployment

Both services include optimized multi-stage `Dockerfile`s for production.

- Set `ENV=production` in your `.env` to enforce strict security policies.
- Ensure the Celery worker (`celery_worker` in `docker-compose.yml`) is running for background email and cleanup tasks.
- Never commit `.env` or `docker-compose.yml` to version control.

---

## 📄 License

**Proprietary / All Rights Reserved.**
Copyright © [Avneesh Mahajan](https://github.com/Avneesh11905). 
You may not copy, fork, modify, distribute, or use this software without explicit written permission.
