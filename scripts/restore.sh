#!/usr/bin/env sh
set -eu

if [ $# -ne 1 ]; then
  echo "Usage: $0 <backup-file.sql>"
  exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "${BACKUP_FILE}" ]; then
  echo "Backup file not found: ${BACKUP_FILE}"
  exit 1
fi

echo "Restoring PostgreSQL database from: ${BACKUP_FILE}"

echo "Dropping and recreating public schema..."
docker compose exec -T db psql \
  -U appuser \
  -d appdb \
  -v ON_ERROR_STOP=1 \
  -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

echo "Applying SQL dump..."
cat "${BACKUP_FILE}" | docker compose exec -T db psql \
  -U appuser \
  -d appdb \
  -v ON_ERROR_STOP=1

echo "Restore completed successfully"