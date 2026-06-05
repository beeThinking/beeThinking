# Production Deployment

This setup targets a Linux server with Docker and a DNS record pointing to the server.

## Files

- `docker-compose.prod.yml` runs Caddy, frontend, backend, PostgreSQL and MinIO.
- `Caddyfile` terminates HTTPS and routes `/api/*` to FastAPI.
- `.env.production.example` documents required production settings.

## First Deploy

```bash
cp .env.production.example .env.production
```

Edit `.env.production`:

- Set `DOMAIN` to the public hostname.
- Replace `SECRET_KEY`, `POSTGRES_PASSWORD` and `MINIO_SECRET_KEY`.
- Set `CORS_ORIGINS=https://your-domain`.

Start:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml up --build -d
```

Check:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml ps
docker compose --env-file .env.production -f docker-compose.prod.yml logs -f backend
curl https://your-domain/health
```

## Updates

```bash
git pull
docker compose --env-file .env.production -f docker-compose.prod.yml up --build -d
```

The backend container runs Alembic migrations before FastAPI starts.

## Network Exposure

Only Caddy publishes ports `80` and `443`. PostgreSQL, backend and MinIO are internal Docker services.
