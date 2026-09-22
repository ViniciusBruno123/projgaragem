# Configuração do gunicorn. Usada pelo serviço systemd (deploy/projgaragem.service).
import multiprocessing
import os

# O nginx conversa com o gunicorn por este socket (ver deploy/nginx.conf).
bind = os.environ.get('GUNICORN_BIND', 'unix:/run/projgaragem/gunicorn.sock')
umask = 0o007  # socket acessível só pelo dono e pelo grupo (www-data, o grupo do nginx)

workers = int(os.environ.get('GUNICORN_WORKERS', min(multiprocessing.cpu_count() * 2 + 1, 5)))
timeout = 60  # upload de fotos grandes + reprocessamento
graceful_timeout = 30
keepalive = 5

# Recicla cada worker de tempos em tempos, contra vazamento de memória.
max_requests = 1000
max_requests_jitter = 100

# Logs vão para a saída padrão: o systemd guarda (journalctl -u projgaragem).
accesslog = '-'
errorlog = '-'
