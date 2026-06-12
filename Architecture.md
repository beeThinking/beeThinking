# BeeThinking Architecture

## Purpose

BeeThinking is a beekeeping management application. It combines hive, apiary, inspection, treatment, feeding, harvest, task, inventory, report, CMS, cashbook and office workflows in one web app.

## Repository Layout

```text
beeThinking/
├── apps/
│   ├── backend/     FastAPI REST API, SQLAlchemy models, Alembic migrations
│   └── frontend/    Angular SPA and PWA shell
├── docker-compose.yml
├── docker-compose.prod.yml
├── Caddyfile
└── *.md             project docs
```

## Runtime Topology

Local Docker stack:

```text
Browser
  |
  v
Angular frontend (nginx, port 80)
  |
  v
FastAPI backend (port 8000)
  |
  +--> PostgreSQL 15 (port 5432)
  |
  +--> MinIO object storage (ports 9000, 9001)
```

Local development can also run split:

- backend: `uvicorn app.main:app --reload`
- frontend: `npm start` on `http://localhost:4200`
- database: PostgreSQL from Docker or a configured `DATABASE_URL`

## Backend

Backend lives in `apps/backend` and uses:

- FastAPI for HTTP API routing
- SQLAlchemy for ORM models and database sessions
- Alembic for schema migrations
- Pydantic/Pydantic Settings for request schemas and environment config
- JWT bearer auth with `python-jose`
- bcrypt for password hashing
- MinIO for photo/object storage
- ReportLab for report/PDF output
- pytest/httpx for tests

Main entrypoint:

- `apps/backend/app/main.py`

Request flow:

```text
FastAPI router
  -> dependency injection
  -> auth/current user checks where required
  -> CRUD/service function
  -> SQLAlchemy session
  -> database/object storage/external provider
  -> Pydantic response schema
```

Backend package roles:

- `app/api`: HTTP routers and endpoint-level validation.
- `app/crud`: database queries and persistence operations.
- `app/models`: SQLAlchemy tables and relationships.
- `app/schemas`: Pydantic input/output contracts.
- `app/services`: domain services and external/provider logic.
- `app/core`: settings and security helpers.
- `app/db`: engine, session factory and declarative base.
- `alembic/versions`: ordered database migrations.

Registered API areas:

- `/api/auth`
- `/api/users`
- `/api/apiaries`
- `/api/hives`
- `/api/hives/{hive_id}/inspections`
- `/api/tasks`
- `/api/treatments`
- `/api/harvests`
- `/api/feedings`
- `/api/articles`
- `/api/inventory-items`
- `/api/queens`
- `/api/photos`
- `/api/dashboard`
- `/api/reports`
- `/api/content`
- `/api/admin/content`
- `/api/cashbook`
- `/api/office`

## Backend Domain Model

Core ownership starts with `User`.

```text
User
  ├── Apiary
  │     ├── Hive
  │     │     ├── Inspection
  │     │     ├── Treatment
  │     │     ├── Feeding
  │     │     ├── Harvest
  │     │     ├── Queen
  │     │     ├── Photo
  │     │     └── HiveEvent
  │     ├── Task
  │     ├── Harvest
  │     ├── Feeding
  │     ├── ApiaryMember
  │     ├── VarroaWeatherWindow
  │     └── CashbookEntry
  ├── InventoryArticle
  ├── InventoryItem
  ├── ContentPage updates
  ├── CashbookEntry
  └── CashbookReceipt
```

Important domain concepts:

- Apiaries represent bee yards/stands and include stock number, address and optional coordinates.
- Hives belong to apiaries and carry lifecycle state such as active, archived, dissolved, merged, sold, dead, inactive, lost or created by mistake.
- Inspections record hive condition, queen state, food stores, varroa count, mood, strength, weather snapshot and next steps.
- Treatments, feedings and harvests model recurring beekeeping operations.
- Inventory has article definitions and concrete inventory items.
- Cashbook and office modules model income, expenses, receipts, reports and EÜR-style summaries.
- CMS content powers public/info pages and admin editing.
- Apiary members provide groundwork for team access.

## Authentication And Authorization

Auth uses OAuth2 password login at `/api/auth/login` and returns JWT access tokens. Frontend stores token in `localStorage` under `access_token`.

Backend dependencies:

- `get_current_user`: validates bearer token and resolves user by username.
- `get_current_active_user`: rejects inactive users.
- `get_current_admin_user`: requires `user.is_admin` or email listed in `ADMIN_EMAILS`.

Frontend guards:

- `authGuard`: protects application routes.
- `adminGuard`: protects admin CMS routes.

## Configuration

Backend settings come from environment variables through `app/core/config.py`.

Required:

- `DATABASE_URL`
- `SECRET_KEY`

Common:

- `APP_NAME`
- `APP_ENV`
- `DEBUG`
- `ADMIN_EMAILS`
- `CORS_ORIGINS`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `MINIO_ENDPOINT`
- `MINIO_ACCESS_KEY`
- `MINIO_SECRET_KEY`
- `MINIO_BUCKET`
- `MINIO_SECURE`
- `VARROA_WEATHER_PROVIDER`
- `VARROA_WEATHER_CACHE_TTL_HOURS`

Production validation rejects known insecure `SECRET_KEY` values when `APP_ENV=production`.

Note: `apps/backend/app/core/config.py` currently declares the Varroa weather setting block twice with different defaults. Python keeps the later declarations.

## Database And Migrations

Database schema is managed by Alembic. FastAPI does not create tables on import.

Common commands from `apps/backend`:

```bash
alembic upgrade head
alembic revision --autogenerate -m "describe change"
```

Docker backend startup runs:

```bash
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Tests often use SQLite via `DATABASE_URL=sqlite:////private/tmp/beethinking_backend_unit.db`.

## Object Storage

Photos and receipt-like binary files are backed by MinIO. Docker starts MinIO with:

- API: `http://localhost:9000`
- Console: `http://localhost:9001`
- bucket: `beethinking-photos`

Backend storage details live in service code under `app/services/storage.py` and photo-related API/CRUD modules.

## Varroa Weather

Varroa weather planning is modeled as a provider-based service.

Provider modules:

- `open_meteo_provider.py`
- `internal_rules_provider.py`
- `official_varroawetter_provider.py`
- `service.py`
- `schemas.py`

Allowed provider names documented in development notes:

- `open_meteo`
- `internal_rules`
- `official_varroawetter`
- `disabled`

No HTML scraping is used. Official Varroawetter integration is a stub until an official endpoint is configured.

## Frontend

Frontend lives in `apps/frontend` and uses:

- Angular 21
- standalone lazy-loaded route components
- RxJS
- Angular signals for auth state
- Angular forms
- Leaflet for maps
- Vitest/jsdom for tests
- Sheriff/ESLint for architecture linting
- PWA manifest and service worker assets in `public`

Main entrypoints:

- `src/main.ts`
- `src/app/app.ts`
- `src/app/app.routes.ts`

Frontend package roles:

- `core/services`: API client and domain-specific service wrappers.
- `core/models`: TypeScript API contracts.
- `core/guards`: auth/admin route guards.
- `core/i18n`: German/English translations.
- `layout`: navbar and footer shell.
- `pages`: feature pages and route components.
- `shared/components`: reusable UI components.

Routing is lazy by page. Public content pages use `InfoPageComponent`; authenticated app routes use `authGuard`; admin CMS uses both `authGuard` and `adminGuard`.

## Frontend Data Flow

```text
Component
  -> domain service
  -> ApiService
  -> HttpClient
  -> FastAPI endpoint
```

`ApiService` composes `environment.apiUrl` with API endpoints. `AuthService` handles login, registration, token storage, current user loading, logout and unauthorized redirects.

## Key Frontend Routes

- `/login`
- `/register`
- `/dashboard`
- `/apiaries` and `/stands`
- `/apiaries/:id` and `/stands/:id`
- `/beehives`
- `/beehives/:id`
- `/beehives/:id/inspect`
- `/hives/archive`
- `/stock-card/:hiveId`
- `/tasks`
- `/harvests`
- `/treatments`
- `/feedings`
- `/honey-harvest`
- `/appointments`
- `/inventory/articles`
- `/inventory/items`
- `/office`
- `/office/cashbook`
- `/office/reports`
- `/admin/cms`
- `/inspections`

## Testing

Backend:

```bash
cd apps/backend
DATABASE_URL=sqlite:////private/tmp/beethinking_backend_unit.db SECRET_KEY=test-secret .venv/bin/pytest tests/unit -q
```

Frontend:

```bash
cd apps/frontend
npm test -- --watch=false
npm run build
```

Development notes list current baseline as:

- backend unit suite: 142 tests
- frontend unit suite: 9 tests across 2 spec files
- Alembic `upgrade head` passes against fresh SQLite database

## Deployment Notes

Docker Compose production config and Caddy config exist at repository root. Local compose exposes frontend on port 80, backend on 8000, PostgreSQL on 5432, MinIO on 9000/9001.

Production-sensitive settings:

- use strong `SECRET_KEY`
- set `APP_ENV=production`
- configure explicit `CORS_ORIGINS`
- use persistent PostgreSQL and MinIO volumes
- run Alembic migrations before serving traffic
- avoid committing `.env` secrets

