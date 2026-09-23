# Colocar no ar (VPS Debian/Ubuntu)

```
Internet ─▶ nginx (HTTPS, fotos em /media/, limite de 20 MB)
              └─▶ gunicorn (socket) ─▶ Django + WhiteNoise (CSS/JS) ─▶ PostgreSQL
cron: inadimplência (diário) · taxa de juros (semanal) · backup (diário)
```

Serve um VPS pequeno (1 vCPU, 1–2 GB de RAM). Antes de começar, tenha:
- o **domínio** com um registro `A` apontando para o IP do servidor;
- uma conta de **SMTP** (o provedor do domínio ou um serviço de envio) para os e-mails de proposta, aviso e erro;
- as credenciais de **produção** do Mercado Pago (as `TEST-` não cobram de verdade).

Convenções abaixo: código em `/srv/projgaragem/app`, ambiente Python em `/srv/projgaragem/venv`, usuário `projgaragem`.
Troque `exemplo.com.br` pelo seu domínio.

## 0. Contratar o servidor e o domínio (você faz, uma vez)

**Servidor (VPS).** Escolha um provedor com **datacenter em São Paulo** (o site abre bem mais rápido para o público de
Catanduva) e cobrança em reais. Confira preço e região no site do provedor antes de pagar; a faixa de entrada costuma
ficar entre R$ 30 e R$ 80 por mês. Configuração: **1 a 2 vCPU, 2 GB de RAM, 20 GB ou mais de disco** e sistema
**Debian 12** ou **Ubuntu 24.04**. Ligue os backups automáticos do provedor, se houver (custam pouco a mais).

**Chave SSH.** Ao criar o servidor, o provedor pergunta como você quer entrar. Escolha "chave SSH" e cole a linha
pública gerada por `ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_vps` (arquivo `~/.ssh/id_ed25519_vps.pub`). Nunca envie o
arquivo sem `.pub`: é a sua chave privada.

**Domínio.** O `.com.br` é registrado em [registro.br](https://registro.br) (cerca de R$ 40 por ano, o mesmo valor na
renovação). Depois de registrar, crie um registro `A` apontando o domínio (e o `www`) para o IP do servidor e espere
propagar (de alguns minutos a poucas horas). Sem domínio não há HTTPS, e o app em produção exige HTTPS.
Para testar antes de comprar o domínio, `IP-COM-TRAÇOS.sslip.io` (por exemplo `203-0-113-10.sslip.io`) aponta sozinho
para o IP e aceita certificado HTTPS.

**Primeiro acesso.**

```bash
ssh -i ~/.ssh/id_ed25519_vps root@IP-DO-SERVIDOR
```

Depois disso, siga as etapas abaixo.

## 1. Servidor

```bash
sudo apt update && sudo apt install -y python3-venv nginx postgresql certbot python3-certbot-nginx git
sudo adduser --system --group --home /srv/projgaragem projgaragem
sudo chmod 755 /srv/projgaragem          # o nginx precisa atravessar a pasta para servir as fotos

sudo ufw allow OpenSSH && sudo ufw allow 'Nginx Full' && sudo ufw enable
```

## 2. Banco de dados

```bash
sudo -u postgres createuser projgaragem
sudo -u postgres createdb -O projgaragem projgaragem
sudo -u postgres psql -c "ALTER USER projgaragem PASSWORD 'UMA-SENHA-FORTE';"
```

## 3. Código

```bash
sudo -u projgaragem git clone https://github.com/ViniciusBruno123/projgaragem.git /srv/projgaragem/app
sudo -u projgaragem python3 -m venv /srv/projgaragem/venv
sudo -u projgaragem /srv/projgaragem/venv/bin/pip install -r /srv/projgaragem/app/requirements.txt
```

## 4. Configuração (`.env`)

```bash
cd /srv/projgaragem/app
sudo -u projgaragem cp .env.production.example .env
sudo -u projgaragem chmod 600 .env
sudo -u projgaragem nano .env       # preencha tudo: cada variável está comentada
```

O app **se recusa a iniciar** em produção se a `SECRET_KEY` for fraca, se faltar `ALLOWED_HOSTS` ou se `SITE_URL`
não começar com `https://`. A mensagem de erro diz o que corrigir.

## 5. Preparar o app

```bash
cd /srv/projgaragem/app
PY=/srv/projgaragem/venv/bin/python
sudo -u projgaragem $PY manage.py migrate
sudo -u projgaragem $PY manage.py collectstatic --noinput
sudo -u projgaragem $PY manage.py createsuperuser
sudo -u projgaragem $PY manage.py atualizar_taxa_media    # sem isso o simulador usa a taxa fixa de 2,00%
sudo -u projgaragem $PY manage.py check --deploy
sudo -u projgaragem mkdir -p media && sudo chmod 755 media
```

O `check --deploy` deve mostrar só 2 avisos (`W005` e `W021`, sobre HSTS para subdomínios e "preload"). São decisões
que só se tomam depois de o HTTPS estar validado; veja o item 9.

## 6. gunicorn (systemd)

```bash
sudo cp deploy/projgaragem.service /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now projgaragem
sudo systemctl status projgaragem          # deve estar "active (running)"
```

Logs: `journalctl -u projgaragem -f`.

## 7. nginx e HTTPS

```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/projgaragem
sudo nano /etc/nginx/sites-available/projgaragem      # troque exemplo.com.br pelo seu domínio
sudo ln -s /etc/nginx/sites-available/projgaragem /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

sudo certbot --nginx -d exemplo.com.br -d www.exemplo.com.br
```

O certbot acrescenta o HTTPS ao mesmo bloco e renova o certificado sozinho.

**Limite de upload:** o `client_max_body_size 20m` do `nginx.conf` precisa ser maior que `FOTO_UPLOAD_MAX_BYTES`
(15 MB, em `settings.py`). Sem ele, o nginx recusa fotos acima de 1 MB com o erro 413, antes de o app ver o arquivo.
Se um dia você aumentar o limite do app, aumente o do nginx junto.

## 8. Rotinas agendadas e backup

```bash
sudo mkdir -p /var/backups/projgaragem && sudo chown projgaragem /var/backups/projgaragem
sudo cp deploy/projgaragem.cron /etc/cron.d/projgaragem
```

O backup (`deploy/backup.sh`) guarda 14 dias de banco e fotos **no próprio servidor**. Copie
`/var/backups/projgaragem` para outro lugar (outro servidor, `rclone` para um bucket): se o servidor for perdido, os
backups vão junto. Saída das rotinas: `journalctl -t projgaragem-cron`.

## 9. Conferir tudo

1. Abra `https://exemplo.com.br/admin/`, entre e cadastre uma garagem de teste com um dono.
2. Entre no painel do dono e **envie uma foto de mais de 5 MB** (testa o limite do nginx e a otimização).
3. Envie uma proposta pela vitrine e veja se o e-mail chega à garagem.
4. Teste o SMTP: `sudo -u projgaragem /srv/projgaragem/venv/bin/python manage.py sendtestemail --admins`.
5. No painel do Mercado Pago, cadastre o webhook `https://exemplo.com.br/billing/webhook/mercadopago/` e copie a
   chave secreta para `MERCADOPAGO_WEBHOOK_SECRET` no `.env`. Depois: `sudo systemctl restart projgaragem`.
6. Depois de alguns dias sem problemas com o HTTPS, suba `SECURE_HSTS_SECONDS` no `.env` de `3600` para `31536000`
   (1 ano). O navegador obedece esse prazo inteiro, então não comece alto.

## Atualizar o site

```bash
cd /srv/projgaragem/app && PY=/srv/projgaragem/venv/bin/python
sudo -u projgaragem git pull
sudo -u projgaragem /srv/projgaragem/venv/bin/pip install -r requirements.txt
sudo -u projgaragem $PY manage.py migrate
sudo -u projgaragem $PY manage.py collectstatic --noinput
sudo systemctl reload projgaragem
```

Isso é tudo: sem tempo de fora do ar perceptível (`reload`, não `restart`, então o gunicorn troca de
processo aos poucos). Se uma migração alterar uma tabela grande, pode demorar mais que o normal —
raro, no volume desta plataforma.

## Manutenção do dia a dia

**Cadastro de garagem/dono, suspender/reativar, gerar link de assinatura** — tudo pelo `/admin/`
(é o painel do administrador da plataforma, diferente do `/painel/` de cada garagem). Não precisa
entrar no servidor por SSH para isso.

**Erros da aplicação** — se `SENTRY_DSN` estiver preenchido no `.env` (opcional, veja
`.env.production.example`), todo erro 500 aparece no painel do [sentry.io](https://sentry.io) com
o stack trace completo, sem precisar entrar no servidor. Sem isso, o administrador recebe só um
e-mail com o erro (`PLATFORM_ADMIN_EMAIL`).

**Logs** — `journalctl -u projgaragem -f` (aplicação, ao vivo) e `journalctl -t projgaragem-cron`
(saída das rotinas agendadas: inadimplência, taxa de juros, backup).

**Backup** — automático todo dia (`deploy/backup.sh`), guarda 14 dias em
`/var/backups/projgaragem`, **no próprio servidor**. Programe uma cópia periódica para fora dali
(outro servidor, `rclone` para um bucket) — se o servidor for perdido, os backups vão junto.

**Certificado HTTPS** — o certbot renova sozinho; não precisa fazer nada, só checar de vez em
quando (`sudo certbot certificates`) se não há aviso de renovação falhando.

**Se você (Vinícius) não quiser mexer no servidor por SSH**, pode voltar aqui e pedir para eu
aplicar uma atualização ou investigar um problema — desde que a chave SSH do servidor esteja
configurada nesta máquina, uso os mesmos comandos deste guia.

## O que este guia não cobre

- Backup **fora** do servidor e teste de restauração (`pg_restore`) — só o automático local.
- Monitoramento de **disponibilidade** (um serviço tipo UptimeRobot avisando se o site cair) —
  o Sentry (se configurado) cobre erros da aplicação, não "o site está fora do ar".
- `fail2ban` ou equivalente para tentativas de acesso por SSH ao próprio servidor (diferente do
  limite de tentativas de login do painel, que já existe — ver `dashboard/security.py`).
