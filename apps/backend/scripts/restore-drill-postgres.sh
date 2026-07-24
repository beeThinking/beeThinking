#!/usr/bin/env sh
set -eu

: "${DATABASE_URL:?DATABASE_URL is required}"
: "${RESTORE_DATABASE_URL:?RESTORE_DATABASE_URL is required}"
: "${PRODUCTION_DATABASE_URL:?PRODUCTION_DATABASE_URL is required to protect the production target}"

[ "$#" -eq 2 ] && [ "$1" = "--confirm-destructive-restore" ] || {
  printf '%s\n' "Usage: restore-drill-postgres.sh --confirm-destructive-restore BACKUP_FILE" >&2
  exit 2
}

backup_file=$2
[ -f "$backup_file" ] || { printf '%s\n' "Backup file does not exist: $backup_file" >&2; exit 2; }

[ "$RESTORE_DATABASE_URL" != "$PRODUCTION_DATABASE_URL" ] || {
  printf '%s\n' "Refusing destructive restore: RESTORE_DATABASE_URL equals PRODUCTION_DATABASE_URL" >&2
  exit 2
}

production_target=$(psql "$PRODUCTION_DATABASE_URL" -Atc "SELECT COALESCE(inet_server_addr()::text, 'local'), inet_server_port(), current_database()")
restore_target=$(psql "$RESTORE_DATABASE_URL" -Atc "SELECT COALESCE(inet_server_addr()::text, 'local'), inet_server_port(), current_database()")
[ "$restore_target" != "$production_target" ] || {
  printf '%s\n' "Refusing destructive restore: restore target resolves to the production database" >&2
  exit 2
}

source_count=$(psql "$DATABASE_URL" -Atc "SELECT count(*) FROM users")
pg_restore --clean --if-exists --no-owner --no-privileges --dbname="$RESTORE_DATABASE_URL" "$backup_file"
restore_count=$(psql "$RESTORE_DATABASE_URL" -Atc "SELECT count(*) FROM users")
[ "$source_count" = "$restore_count" ] || { printf '%s\n' "Restore row-count mismatch: users source=$source_count restore=$restore_count" >&2; exit 1; }
printf '%s\n' "Restore row-count verified: users=$restore_count"
