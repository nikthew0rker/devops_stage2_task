#!/usr/bin/env sh
set -eu

mkdir -p backups

TS="$(date +%Y%m%d_%H%M%S)"
BACKUP_FILE="backups/appdb_${TS}.sql"

echo "Creating PostgreSQL backup: ${BACKUP_FILE}"

docker compose exec -T db pg_dump \
  -U appuser \
  -d appdb \
  > "${BACKUP_FILE}"

test -s "${BACKUP_FILE}" || {
  echo "Backup file is empty or was not created"
  exit 1
}

echo "Backup completed successfully: ${BACKUP_FILE}"