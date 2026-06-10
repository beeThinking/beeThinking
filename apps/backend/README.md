# BeeThinking Backend

FastAPI backend for BeeThinking. Provides authentication, apiary and hive management, inspections, feeding, treatments, harvests, inventory, reports, CMS content and cashbook APIs.

## Stack

- Python 3.11+
- FastAPI
- SQLAlchemy
- Alembic
- JWT authentication
- SQLite for local development
- PostgreSQL for Docker/production
- MinIO-compatible object storage for photos

## Setup

```bash
cd apps/backend
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

API docs:

- http://localhost:8000/docs
- http://localhost:8000/redoc

## Environment

Required:

```env
DATABASE_URL=sqlite:///./beethinking.db
SECRET_KEY=replace-with-a-long-random-secret
```

Common optional settings:

```env
DEBUG=True
CORS_ORIGINS=http://localhost:4200,http://localhost
ACCESS_TOKEN_EXPIRE_MINUTES=30
EMAIL_CONFIRMATION_ENABLED=False
VARROA_WEATHER_PROVIDER=open_meteo
```

## Migrations

Run Alembic commands from `apps/backend`:

```bash
alembic upgrade head
alembic revision --autogenerate -m "describe change"
alembic current
```

The application does not create tables on import. Docker startup runs `alembic upgrade head` before Uvicorn starts.

## API Areas

Public:

- `GET /`
- `GET /health`
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/content/pages/{slug}?locale=de`

Authenticated:

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
- `/api/admin/content`
- `/api/cashbook`

## Tests

```bash
pytest
pytest apps/backend/tests/unit -q
```

Current unit suite: 142 tests.

## Docker

From repository root:

```bash
docker-compose up --build
```

Production deployment uses `docker-compose.prod.yml`; see [../../DEPLOYMENT.md](../../DEPLOYMENT.md).

License: [MIT](../../LICENSE).
