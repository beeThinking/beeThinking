# Production PostgreSQL backups

Backups run from the production host, never from CI. Configure the host cron with production-only environment variables:

```cron
0 2 * * * DATABASE_URL='postgresql://...' BACKUP_DIR=/srv/beethinking/backups /srv/beethinking/apps/backend/scripts/backup-postgres.sh >> /var/log/beethinking-backup.log 2>&1
```

Retain and copy encrypted backup files according to the production retention policy. A monthly restore drill must restore into an isolated database and verify the `users` row count:

```sh
DATABASE_URL='postgresql://production-readonly...' PRODUCTION_DATABASE_URL='postgresql://production...' RESTORE_DATABASE_URL='postgresql://restore-target...' ./scripts/restore-drill-postgres.sh --confirm-destructive-restore /srv/beethinking/backups/beethinking-YYYYMMDDTHHMMSSZ.dump
```

`pg_restore --clean` deletes objects in the restore target. The confirmation flag is mandatory. `PRODUCTION_DATABASE_URL` is mandatory even when `DATABASE_URL` is read-only; the script rejects both an identical URL and a target which resolves to the same PostgreSQL server, port, and database as production. Use a separate database on a separate restore environment.

There is no SQLite restore script. The scripts require PostgreSQL client tools (`pg_dump`, `pg_restore`, and `psql`) on the production host.

## Reverse proxy rate limiting

By default, authentication rate limits use the direct remote address and ignore `X-Forwarded-For`. Set `TRUST_PROXY_HEADERS=True` only behind a reverse proxy that removes every client-supplied forwarding header and writes its own. Set `TRUSTED_PROXY_IPS` to the comma-separated addresses of those proxies; forwarded addresses are ignored unless the direct peer is in that list.
