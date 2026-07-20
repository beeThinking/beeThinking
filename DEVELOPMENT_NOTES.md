# Development Notes

## Start Commands

Full stack from repository root:

```bash
docker-compose up --build
```

Backend locally:

```bash
cd apps/backend
cp .env.example .env
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Frontend locally:

```bash
cd apps/frontend
npm install
npm start
```

## Ports

- Frontend Docker: http://localhost
- Frontend dev server: http://localhost:4200
- Backend: http://localhost:8000
- API docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432

## Test Commands

Backend:

```bash
cd apps/backend
pytest
DATABASE_URL=sqlite:////private/tmp/beethinking_backend_unit.db SECRET_KEY=test-secret .venv/bin/pytest tests/unit -q
```

Frontend:

```bash
cd apps/frontend
npm run lint
npm test -- --watch=false
npm run build
```

## Database Migrations

Schema changes are managed by Alembic from `apps/backend`:

```bash
alembic upgrade head
alembic revision --autogenerate -m "describe change"
```

FastAPI no longer creates tables on import. Docker runs migrations before Uvicorn starts.

## Varroa Weather

Varroa weather windows use a normal weather provider plus maintained treatment rules. Default production provider is Open-Meteo:

```bash
VARROA_WEATHER_PROVIDER=open_meteo
VARROA_WEATHER_CACHE_TTL_HOURS=6
```

Allowed providers: `open_meteo`, `internal_rules`, `official_varroawetter`, `disabled`.

No HTML scraping is used. `official_varroawetter` is a stub until an official API endpoint is configured and documented.

## Google Calendar

Appointment mirroring uses a dedicated secondary Google Calendar and the least-privilege
`calendar.app.created` OAuth scope. Configure a Google OAuth web client with this redirect URI:

```text
http://localhost:8000/api/google-calendar/oauth/callback
```

Set `GOOGLE_CALENDAR_CLIENT_ID`, `GOOGLE_CALENDAR_CLIENT_SECRET`, and
`GOOGLE_CALENDAR_TOKEN_KEY` in the backend `.env`. `GOOGLE_CALENDAR_TOKEN_KEY` is required
in every environment as soon as a client ID is configured — refresh tokens are encrypted
with it at rest (no `SECRET_KEY` fallback). Disconnecting revokes the token but keeps the
mirrored Google calendar and its events.

## Current Verification Baseline

- Backend unit suite: 217 tests.
- Frontend unit suite: 57 tests across 13 spec files.
- Alembic `upgrade head` passes against a fresh SQLite database.
