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
```

Frontend:

```bash
cd apps/frontend
npm run lint
npm run test -- --run
npm run build
```

## Database Migrations

Schema changes are managed by Alembic from `apps/backend`:

```bash
alembic upgrade head
alembic revision --autogenerate -m "describe change"
```

FastAPI no longer creates tables on import. Docker runs migrations before Uvicorn starts.

## Known Issues

- Full Docker startup and manual register/login have not been rechecked in this pass.
