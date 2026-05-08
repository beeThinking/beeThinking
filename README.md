# BeeThinking

Monorepo for the BeeThinking application.

## Structure

```
beeThinking/
├── apps/
│   ├── backend/    # FastAPI (Python)
│   └── frontend/   # Angular
└── docker-compose.yml
```

## Getting started

### Backend

```bash
cd apps/backend
cp .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd apps/frontend
npm install
npm start
```

### Docker (full stack)

```bash
docker-compose up
```
