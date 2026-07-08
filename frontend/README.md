<div align="center">

<img src="https://cerberus.aymahajan.in/logo.webp" alt="Cerberus Logo" width="80" />

# Cerberus Dashboard

**The project management interface for the Cerberus Identity Platform.**

[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-6.x-646CFF?style=flat-square&logo=vite&logoColor=white)](https://vitejs.dev/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](../LICENSE)

</div>

---

> **Building your own app?** This is the management dashboard — not the integration SDK. To integrate Cerberus authentication into your frontend, use the official **[TypeScript SDK](https://github.com/Avneesh11905/cerberus-sdk)**.

---

## ✨ What You Can Do

- **Create & manage Projects** — Isolate your users and configuration per project.
- **API Key management** — Keys are shown **once** on creation/rotation and stored only as hashes. Rotate anytime.
- **OAuth configuration** — Add your own Google / GitHub credentials per project, directly from the UI.
- **Allowed Origins** — Dynamically whitelist frontend URLs for secure cross-origin cookie support.
- **Environment toggle** — Switch between Development (no rate limits) and Production mode per project.
- **Session management** — View active sessions and remotely revoke devices.
- **Profile & security settings** — Update display name, avatar, password, and manage active sessions.

---

## 🚀 Getting Started

### Prerequisites
- **Node.js** 20+
- Cerberus backend running on `http://localhost:8000`

### Setup

```bash
# Install dependencies
npm install

# Create environment file
echo "VITE_API_URL=http://localhost:8000" > .env

# Start dev server
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000).

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| Framework | [Vite](https://vitejs.dev/) + [TanStack Router](https://tanstack.com/router) (file-based routing) |
| UI Components | [Shadcn UI](https://ui.shadcn.com/) (`radix-ui`) |
| Styling | Tailwind CSS v4 |
| Icons | Lucide React |
| HTTP Client | Axios (with silent token refresh interceptor) |
| State / Data | TanStack Query |

---

## 📂 Project Structure

```
frontend/
├── src/
│   ├── components/       # Reusable UI components
│   │   └── ui/           # Shadcn primitives
│   ├── hooks/            # Custom React hooks (useProjects, useAuth, etc.)
│   ├── lib/              # Axios instance, auth context, utilities
│   ├── routes/           # File-based routing (TanStack Router)
│   │   ├── auth/         # Login, Register, OAuth callback
│   │   ├── _protected.*  # Authenticated routes (Dashboard, Settings, Projects)
│   │   └── docs.*        # Documentation pages
│   └── styles.css        # Global styles
└── public/               # Static assets
```

---

## 🔐 API Key Security Model

API keys are **never stored in plaintext**. Only a SHA-256 hash is persisted in the database.

| Moment | What the UI shows |
|---|---|
| Project created / key rotated | Full key displayed **once** with a "Save this now" warning |
| Every subsequent visit | Masked display: `cerb_XXXXXXXXXX` |

If a key is lost, use the **Rotate API Key** button to invalidate the old key and receive a new one.

---

## 🛠️ Authentication Architecture

The dashboard integrates directly with the Cerberus API using `src/lib/api.ts`:

- **Silent Token Refresh:** The Axios interceptor catches `401 Unauthorized` responses, calls `POST /auth/refresh` using the `HttpOnly` cookie, and transparently retries the failed request.
- **CSRF Protection:** The `csrf_token` is returned in the JSON body of `/auth/refresh` and `/auth/exchange` responses, stored in memory, and attached as the `X-CSRF` header on all state-changing requests.

---

## 📦 Building for Production

```bash
npm run build
```

Ensure `VITE_API_URL` is set to your production backend URL at build time.

---

## 📄 License

MIT © [Avneesh Mahajan](https://github.com/Avneesh11905)
