# Backup and Restore

Back up PostgreSQL, MinIO data and `.env.production`. Store `.env.production` separately from public source control.

## Backup

```bash
mkdir -p backups
docker compose --env-file .env.production -f docker-compose.prod.yml exec -T db pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > backups/beethinking.sql
docker run --rm -v beethinking_minio_data:/data -v "$PWD/backups:/backup" alpine tar czf /backup/minio-data.tgz -C /data .
cp .env.production backups/env.production.backup
```

## Restore

Stop the stack before restoring volumes:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml down
```

Restore PostgreSQL after the database container is running:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml up -d db
cat backups/beethinking.sql | docker compose --env-file .env.production -f docker-compose.prod.yml exec -T db psql -U "$POSTGRES_USER" "$POSTGRES_DB"
```

Restore MinIO data:

```bash
docker run --rm -v beethinking_minio_data:/data -v "$PWD/backups:/backup" alpine sh -c "cd /data && tar xzf /backup/minio-data.tgz"
```

Then start the full stack:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml up -d
```
