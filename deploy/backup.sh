#!/usr/bin/env bash
# Backup diário: banco de dados + fotos. Mantém 14 dias.
# ATENÇÃO: isto guarda cópias no próprio servidor. Copie /var/backups/projgaragem para FORA
# (outro servidor, rclone para um bucket...): se o servidor for perdido, os backups vão junto.
set -euo pipefail

APP=/srv/projgaragem/app
DESTINO=/var/backups/projgaragem
DATA=$(date +%F)

# Lê só o DATABASE_URL: o .env tem caracteres (como $ e !) que não podem ser "sourced" no bash.
DATABASE_URL=$(grep -E '^DATABASE_URL=' "$APP/.env" | cut -d= -f2-)

mkdir -p "$DESTINO"
pg_dump --format=custom --file="$DESTINO/banco-$DATA.dump" "$DATABASE_URL"
tar -czf "$DESTINO/fotos-$DATA.tar.gz" -C "$APP" media
find "$DESTINO" -type f -mtime +14 -delete

echo "Backup de $DATA concluído em $DESTINO"
