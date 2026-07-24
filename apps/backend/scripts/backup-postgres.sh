#!/usr/bin/env sh
set -eu

: "${DATABASE_URL:?DATABASE_URL is required}"
: "${BACKUP_DIR:?BACKUP_DIR is required}"

mkdir -p "$BACKUP_DIR"
timestamp=$(date -u +%Y%m%dT%H%M%SZ)
output="$BACKUP_DIR/beethinking-$timestamp.dump"
pg_dump --format=custom --no-owner --no-privileges --file="$output" "$DATABASE_URL"
printf '%s\n' "$output"
