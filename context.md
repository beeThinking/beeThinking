# BeeThinking Context

## Project Summary

BeeThinking is a full-stack beekeeping management app. Main users are beekeepers managing apiaries, hives, inspections, treatments, feedings, harvests, tasks, inventory, photos, reports, CMS content, cashbook and office workflows.

The repo is a monorepo:

- backend: `apps/backend`
- frontend: `apps/frontend`
- infrastructure/docs: repository root

## Current Stack

Backend:

- Python 3.11+
- FastAPI
- SQLAlchemy
- Alembic
- Pydantic v2
- JWT auth
- PostgreSQL in Docker
- SQLite for many local/unit test runs
- MinIO object storage
- pytest

Frontend:

- Angular 21
- TypeScript 5.9
- RxJS
- Angular standalone components and lazy routes
- Angular signals for auth state
- Leaflet maps
- Vitest/jsdom tests
- ESLint/Sheriff architecture linting

Infrastructure:

- Docker Compose for local full stack
- nginx container for frontend image
- Caddy config present for deployment
- MinIO for object storage

## Important Commands

Full stack:

```bash
docker-compose up --build
```

Backend local:

```bash
cd apps/backend
cp .env.example .env
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Frontend local:

```bash
cd apps/frontend
npm install
npm start
```

Backend tests:

```bash
cd apps/backend
DATABASE_URL=sqlite:////private/tmp/beethinking_backend_unit.db SECRET_KEY=test-secret .venv/bin/pytest tests/unit -q
```

Frontend checks:

```bash
cd apps/frontend
npm test -- --watch=false
npm run build
```

Migrations:

```bash
cd apps/backend
alembic upgrade head
alembic revision --autogenerate -m "describe change"
```

## Local URLs

- frontend Docker: `http://localhost`
- frontend dev server: `http://localhost:4200`
- backend: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- PostgreSQL: `localhost:5432`
- MinIO API: `http://localhost:9000`
- MinIO console: `http://localhost:9001`

## Domain Vocabulary

- Apiary/Stand: location where hives are kept.
- Stock number: identifier associated with apiary/stand records.
- Hive/Volk: managed bee colony.
- Inspection/Durchschau: structured hive check with condition, queen, food, varroa, weather and next steps.
- Treatment: beekeeping treatment action, especially Varroa-related.
- Feeding: sugar/feed action for hive or apiary.
- Harvest: honey harvest record.
- Queen: queen tracking for a hive.
- Task: beekeeper task or appointment-like work item.
- Inventory article: reusable item definition.
- Inventory item: concrete stock/inventory entry.
- Cashbook/Kassenbuch: income, expenses, receipts and accounting summary.
- Office/Büro: cashbook and reporting area.
- CMS content: editable public/info page content.

## Coding Patterns

Backend pattern:

1. Add/update SQLAlchemy model in `app/models`.
2. Add/update Pydantic schemas in `app/schemas`.
3. Add/update CRUD functions in `app/crud`.
4. Add/update HTTP router in `app/api`.
5. Register router in `app/main.py` when adding new API area.
6. Add Alembic migration in `alembic/versions`.
7. Add tests under `tests/unit` or `tests/integration`.

Frontend pattern:

1. Add/update TypeScript models in `core/models`.
2. Add/update API calls in `core/services`.
3. Add/update route component under `pages`.
4. Register route in `app.routes.ts`.
5. Add/adjust translations in `core/i18n/de.ts` and `core/i18n/en.ts`.
6. Add tests where behavior is non-trivial or shared.

API pattern:

- Endpoints use `/api/...` prefixes from `app/main.py`.
- Authenticated endpoints depend on current active user.
- Admin endpoints require `get_current_admin_user`.
- Backend returns Pydantic schemas, not raw ORM objects unless FastAPI schema conversion is intentional.

## Auth Context

Login endpoint is `/api/auth/login`. Frontend sends OAuth2 password form data and stores returned bearer token in `localStorage` as `access_token`.

User state lives in `AuthService`:

- `isAuthenticated`
- `currentUser`
- `isAdmin`

Protected frontend routes use `authGuard`. Admin CMS route uses both `authGuard` and `adminGuard`.

Backend admin status comes from either:

- `User.is_admin`
- email listed in `ADMIN_EMAILS`

## Data And Persistence

Primary relational database is PostgreSQL. SQLAlchemy models are source for runtime ORM; Alembic migrations are source for schema changes.

Never rely on FastAPI startup to create tables. Run migrations.

Binary/photo storage goes through MinIO-backed service code. Do not store large binary payloads directly in PostgreSQL unless schema explicitly says so.

## External Providers

Varroa weather uses provider abstraction under `app/services/varroa_weather`.

Known provider names:

- `open_meteo`
- `internal_rules`
- `official_varroawetter`
- `disabled`

Current policy from docs: no HTML scraping. Official Varroawetter provider stays stubbed until official API details are configured and documented.

## Environment Notes

Backend requires at least:

- `DATABASE_URL`
- `SECRET_KEY`

Docker overrides `DATABASE_URL` to Postgres service URL and MinIO endpoint to `minio:9000`.

Production must set secure `SECRET_KEY`. `APP_ENV=production` validates against known placeholder secrets.

Potential config caveat: `apps/backend/app/core/config.py` currently repeats the Varroa weather fields; later Python class declarations win.

## Current Worktree Note

As of this documentation pass, worktree already contained many modified and untracked files across backend, frontend, migrations and tests. Treat those as existing user/project changes unless explicitly told otherwise.

## Useful Files

- `README.md`: quick start, features, test commands.
- `DEVELOPMENT_NOTES.md`: ports, test baseline, Varroa provider notes.
- `DEPLOYMENT.md`: deployment guidance.
- `BACKUP.md`: backup/restore notes.
- `apps/backend/README.md`: backend-specific docs.
- `apps/frontend/README.md`: frontend-specific docs.
- `apps/backend/app/main.py`: API router registration.
- `apps/backend/app/core/config.py`: backend settings.
- `apps/frontend/src/app/app.routes.ts`: frontend route map.
- `apps/frontend/src/app/core/services/api.service.ts`: HTTP wrapper.
- `apps/frontend/src/app/core/services/auth.service.ts`: frontend auth state.

## Maintenance Rules

- Keep docs synchronized when routes, modules, environment variables or runtime topology change.
- Add Alembic migrations for schema changes.
- Prefer existing API/service/model structure over introducing new patterns.
- Keep frontend routes lazy-loaded unless there is a reason not to.
- Keep auth and admin checks explicit at route/API boundaries.
- Run focused backend/frontend checks after behavior changes.
- Do not commit `.env` secrets.

