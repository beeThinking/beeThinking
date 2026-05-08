# CLAUDE.md — BeeThinking Monorepo

This file provides context and conventions for AI coding assistants (Claude / OpenCode) working in this repository.

---

## Project Overview

BeeThinking is a beekeeping management application. It consists of:

- **Backend** (`apps/backend/`) — REST API built with FastAPI, SQLAlchemy, and JWT authentication
- **Frontend** (`apps/frontend/`) — Single-page application built with Angular 21

The full stack can be started with `docker-compose up` from the repository root.

---

## Repository Structure

```
beeThinking/
├── apps/
│   ├── backend/          # Python / FastAPI
│   │   ├── app/
│   │   │   ├── api/      # Route handlers (auth.py, users.py, dependencies.py)
│   │   │   ├── core/     # Config (pydantic-settings) and security (JWT, bcrypt)
│   │   │   ├── crud/     # Database operations
│   │   │   ├── db/       # SQLAlchemy engine and session
│   │   │   ├── models/   # ORM models
│   │   │   ├── schemas/  # Pydantic request/response schemas
│   │   │   └── main.py   # FastAPI app, CORS, router registration
│   │   ├── tests/
│   │   │   ├── unit/     # Isolated unit tests
│   │   │   └── integration/  # End-to-end API tests
│   │   ├── requirements.txt
│   │   └── .env.example
│   └── frontend/         # Angular 21
│       └── src/app/
│           ├── core/     # Guards, interceptors, services, models
│           ├── layout/   # Navbar, footer
│           ├── pages/    # Feature pages (dashboard, beehives, login, register, …)
│           └── shared/   # Reusable components
├── .github/
│   ├── workflows/        # CI: backend.yml (pytest), frontend.yml (lint+test+build)
│   ├── ISSUE_TEMPLATE/   # Bug report and feature request forms
│   └── pull_request_template.md
├── CONTRIBUTING.md
├── CHANGELOG.md
├── SECURITY.md
├── CODE_OF_CONDUCT.md
└── docker-compose.yml
```

---

## Tech Stack

### Backend
| Concern | Library |
|---|---|
| Framework | FastAPI |
| ORM | SQLAlchemy 2.x |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Auth | JWT (`python-jose`), bcrypt (`passlib`) |
| Settings | `pydantic-settings` via `.env` |
| Server | Uvicorn |
| Tests | pytest + pytest-asyncio + httpx |
| Database (dev) | SQLite |
| Database (prod) | PostgreSQL 15 |

### Frontend
| Concern | Library |
|---|---|
| Framework | Angular 21 (standalone components) |
| Language | TypeScript 5.9 |
| Tests | Vitest + jsdom + Angular TestBed |
| Linting | ESLint + angular-eslint |
| Architecture | Sheriff (module boundaries) |
| HTTP | Angular `HttpClient` + auth interceptor |
| Routing | Angular Router + auth guard |

---

## Development Commands

### Backend
```bash
cd apps/backend
cp .env.example .env          # first time only
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload  # http://localhost:8000
pytest                         # run all tests
pytest -m unit                 # unit tests only
pytest -m integration          # integration tests only
pytest --cov=app               # with coverage
```

### Frontend
```bash
cd apps/frontend
npm install                    # first time only
npm start                      # http://localhost:4200
npm test                       # Vitest unit tests
npm run lint                   # ESLint
npm run build                  # production build → dist/bee-thinking/
```

### Full stack
```bash
docker-compose up              # starts db + backend (8000) + frontend (80)
docker-compose up --build      # rebuild images first
```

---

## Code Conventions

### General
- All identifiers, comments, commit messages, and PR descriptions must be in **English**.
- Do not write JSDoc or inline comments unless explicitly requested.
- Prefer editing existing files over creating new ones.
- Do not commit secrets or credentials. Sensitive values belong in `.env` (git-ignored).

### Backend (Python)
- Follow the existing layered structure: `api → crud → models/schemas`.
- Route handlers live in `app/api/`. Keep them thin — business logic goes in `crud/` or `core/`.
- All settings are read through `get_settings()` from `app/core/config.py`. Never hardcode config values.
- New endpoints need at least one unit test in `tests/unit/test_api/`.
- Use `Depends(get_db)` for database sessions — never create sessions manually in handlers.

### Frontend (Angular)
- Use **standalone components** (no NgModules).
- All new files go under the appropriate `core/`, `pages/`, `shared/`, or `layout/` directory.
- Services use Angular's `inject()` function, not constructor injection.
- HTTP calls go through `ApiService` (`core/services/api.service.ts`).
- Authentication state is managed by `AuthService` (`core/services/auth.service.ts`).
- Always import Vitest globals explicitly (`describe`, `it`, `expect`, `vi`, `beforeEach`) in spec files — do not rely on globals config.

### Frontend — Mobile-first CSS (IMPORTANT)
The entire frontend follows a **mobile-first** CSS approach. This is a hard convention — never break it.

Rules:
- **Write base styles for the smallest screen first** (≥ 320 px). Add `@media (min-width: …)` overrides for larger screens. Never use `max-width` media queries.
- **Breakpoints** (defined as CSS custom properties in `styles.css`):
  - `480px` — sm (phablet)
  - `768px` — md (tablet / small desktop)
  - `1024px` — lg (desktop)
- **Spacing** — use the CSS custom property scale (`--space-xs` … `--space-2xl`) and `--page-px` (fluid horizontal padding). Never hardcode `px` spacing in component CSS.
- **Touch targets** — all interactive elements must be at least **44 × 44 px** (`min-height: 44px`). Enforced globally in `styles.css`.
- **Font sizes** — use `clamp()` for headings so they scale fluidly. Set `font-size: 1rem` (16px) on inputs to prevent iOS auto-zoom on focus.
- **Modals** — on mobile (< 768 px) modals render as a **bottom sheet** (`align-items: flex-end`, `border-radius: 16px 16px 0 0`). On desktop they are centered overlays.
- **Hover effects** — wrap hover styles in `@media (hover: hover)` so they are not triggered on touch devices.
- **Scrollable containers** — add `-webkit-overflow-scrolling: touch` and `scrollbar-width: none` for horizontal scroll areas (e.g. hive tab bar).
- Do **not** import `CommonModule` — use Angular 17+ built-in control flow (`@if`, `@for`, `@switch`) instead.
- `ChangeDetectionStrategy.OnPush` is mandatory on every component.

---

## Architecture Decisions

### Authentication
- JWT tokens stored in `localStorage` on the frontend.
- The `AuthInterceptor` (`core/interceptors/auth.interceptor.ts`) automatically attaches the Bearer token to outgoing requests.
- The `AuthGuard` (`core/guards/auth.guard.ts`) protects routes requiring login.
- Backend token expiry: 30 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES` in `.env`).

### Database
- Development default: SQLite (`DATABASE_URL=sqlite:///./beethinking.db`).
- Production: PostgreSQL 15 (configured in `docker-compose.yml`).
- Tables are auto-created on startup via `Base.metadata.create_all()`. For schema changes, use Alembic migrations.

### Testing (Frontend)
- Test runner: **Vitest** (not Karma/Jest). Config: `apps/frontend/vitest.config.ts`.
- Environment: jsdom, initialized via `src/test-setup.ts`.
- DOM tests use `fixture.nativeElement` — see existing examples in `login.component.spec.ts`.

---

## Commit Convention

```
<ticket-number> - <short description>

Optional sections:
* Breaking Changes
* Critical Changes
* Bugfixes
```

Example: `42 - add beehive inspection endpoint`

---

## Important Decisions Log

Decisions that required investigation or are non-obvious are recorded in `apps/frontend/AI_DOCS/`. Check there before changing the test setup or Angular configuration.
