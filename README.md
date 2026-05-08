# BeeThinking

A beekeeping management application — think like a bee.

## Structure

```
beeThinking/
├── apps/
│   ├── backend/    # REST API — FastAPI, SQLAlchemy, JWT (Python 3.11+)
│   └── frontend/   # SPA — Angular 21
└── docker-compose.yml
```

## Quick Start

### Full stack with Docker

```bash
docker-compose up
```

| Service  | URL                        |
|----------|----------------------------|
| Frontend | http://localhost            |
| Backend  | http://localhost:8000       |
| API Docs | http://localhost:8000/docs  |

### Backend (local)

```bash
cd apps/backend
cp .env.example .env        # configure SECRET_KEY and DATABASE_URL
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend (local)

```bash
cd apps/frontend
npm install
npm start                   # http://localhost:4200
```

## Apps

| App | Readme |
|-----|--------|
| Backend | [apps/backend/README.md](apps/backend/README.md) |
| Frontend | [apps/frontend/README.md](apps/frontend/README.md) |
