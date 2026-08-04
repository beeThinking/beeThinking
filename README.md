# BeeThinking

A beekeeping management application — think like a bee.

## Features

- Apiaries, hives, inspections and hive lifecycle history
- Durchschau workflow with inspections, feeding, treatments and harvests
- Tasks, appointments, inventory, photos and reports
- Direct Google Calendar mirroring for appointments
- Team apiary invitations and role-based collaboration
- CMS-backed public content pages with admin editing UI
- Cashbook with income, expenses and EÜR summary
- PWA shell and local inspection drafts

See [ROADMAP.md](ROADMAP.md) for the development plan.

## Structure

```
beeThinking/
├── apps/
│   ├── backend/    # REST API — FastAPI, SQLAlchemy, JWT (Python 3.11+)
│   ├── frontend/   # SPA — Angular 21
│   └── mobile/     # iOS-first client — Flutter (Android later)
└── docker-compose.yml
```

## Quick Start

### Full stack with Docker

**First time only** — create the backend `.env` file:

```bash
cp apps/backend/.env.example apps/backend/.env
```

Then start the stack:

```bash
docker-compose up
```

| Service  | URL                        |
|----------|----------------------------|
| Frontend | http://localhost            |
| Backend  | http://localhost:8000       |
| API Docs | http://localhost:8000/docs  |

### Rebuilding after code changes

| Situation | Command |
|---|---|
| Code changed | `docker-compose up --build` |
| Container still running | `docker-compose down && docker-compose up --build` |
| Dependency changed (`requirements.txt` / `package.json`) | `docker-compose build --no-cache && docker-compose up` |
| Reset database volume | `docker-compose down -v && docker-compose up --build` |

> **Warning:** `-v` deletes the Postgres volume — all data will be lost.

### Backend (local)

```bash
cd apps/backend
cp .env.example .env        # configure SECRET_KEY and DATABASE_URL
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend (local)

```bash
cd apps/frontend
npm install
npm start                   # http://localhost:4200
```

### Mobile (local)

The Flutter client currently targets iOS. Android support is planned; Flutter Web is not supported. Install Flutter `3.24.5` and Xcode, then run:

```bash
flutter --directory apps/mobile pub get
flutter --directory apps/mobile run
```

Debug builds use `http://localhost:8000` by default. Override the API endpoint at build time with `--dart-define=API_BASE_URL=https://api.example.com`; non-debug builds require it. See the [mobile README](apps/mobile/README.md) for configuration details.

The mobile app runs outside Docker and is not part of either Compose stack.

## Apps

| App | Readme |
|-----|--------|
| Backend | [apps/backend/README.md](apps/backend/README.md) |
| Frontend | [apps/frontend/README.md](apps/frontend/README.md) |
| Mobile | [apps/mobile/README.md](apps/mobile/README.md) |

## Login

There are no pre-seeded demo accounts. Create your account on the Register page (`/register`) with any username, email and a password of at least 8 characters.

**Example:**

| Field    | Value              |
|----------|--------------------|
| Username | `beekeeper`        |
| Email    | `bee@example.com`  |
| Password | `MyBees2025!`      |

After registering you are redirected to the login page (`/login`) and can sign in immediately.

## Database Migrations

The backend uses Alembic for schema migrations. Run migration commands from `apps/backend`:

```bash
alembic upgrade head
alembic revision --autogenerate -m "describe change"
```

The Docker backend container runs `alembic upgrade head` before starting FastAPI.

## Checks

```bash
cd apps/backend
DATABASE_URL=sqlite:////private/tmp/beethinking_backend_unit.db SECRET_KEY=test-secret .venv/bin/pytest tests/unit -q

cd ../frontend
npm test -- --watch=false
npm run build

cd ../mobile
dart format --output=none --set-exit-if-changed .
flutter analyze
flutter test
flutter build ios --release --no-codesign --dart-define=API_BASE_URL=https://api.example.com
```
