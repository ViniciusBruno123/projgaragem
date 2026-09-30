#!/usr/bin/env bash
# Backup diário: banco de dados + fotos. Mantém 14 dias local e no bucket remoto.
# Guarda uma cópia no próprio servidor E envia para um bucket (rclone), para sobreviver
# à perda do servidor. Sem remote "b2backup" configurado (rclone config), pula o envio
# remoto silenciosamente — configure com: rclone config create b2backup b2 account KEY_ID key APP_KEY
set -euo pipefail

APP=/srv/projgaragem/app
DESTINO=/var/backups/projgaragem
DATA=$(date +%F)
REMOTO=b2backup:spitechfarol

# cd para uma pasta que o usuário projgaragem realmente acessa: sem isso, rodando via "sudo -u
# projgaragem" a partir do home do root (/root), comandos como "find -delete" falham ao tentar
# voltar pro diretório de origem (Permission denied) e abortam o script inteiro por causa do -e.
cd "$APP"

# Lê só o DATABASE_URL: o .env tem caracteres (como $ e !) que não podem ser "sourced" no bash.
DATABASE_URL=$(grep -E '^DATABASE_URL=' "$APP/.env" | cut -d= -f2-)

mkdir -p "$DESTINO"
pg_dump --format=custom --file="$DESTINO/banco-$DATA.dump" "$DATABASE_URL"
tar -czf "$DESTINO/fotos-$DATA.tar.gz" -C "$APP" media
find "$DESTINO" -type f -mtime +14 -delete

if command -v rclone >/dev/null && rclone listremotes | grep -q "^b2backup:"; then
    rclone copy "$DESTINO/banco-$DATA.dump" "$REMOTO/"
    rclone copy "$DESTINO/fotos-$DATA.tar.gz" "$REMOTO/"
    rclone delete --min-age 14d "$REMOTO/" || true
    echo "Backup de $DATA concluído em $DESTINO e enviado para $REMOTO"
else
    echo "Backup de $DATA concluído em $DESTINO (rclone/remote 'b2backup' não configurado — sem cópia remota)"
fi
