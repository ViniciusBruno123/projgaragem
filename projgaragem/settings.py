"""
Django settings for projgaragem project.

Toda a configuração vem de variáveis de ambiente (arquivo .env na raiz do projeto).
Em desenvolvimento, DEBUG=True. Em produção veja deploy/README.md e .env.production.example.
"""

import re
from decimal import Decimal
from pathlib import Path

import environ
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY")

DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

SITE_URL = env('SITE_URL', default='http://localhost:8000')

# Em produção, falha logo na partida (com mensagem clara) em vez de subir inseguro.
if not DEBUG:
    if SECRET_KEY.startswith('django-insecure') or SECRET_KEY == 'change-me' or len(SECRET_KEY) < 50:
        raise ImproperlyConfigured(
            "SECRET_KEY de produção precisa ser própria e ter ao menos 50 caracteres. Gere uma com: "
            "python -c \"from django.core.management.utils import get_random_secret_key as g; print(g())\""
        )
    if not ALLOWED_HOSTS:
        raise ImproperlyConfigured("Defina ALLOWED_HOSTS com o domínio do site (ex: ALLOWED_HOSTS=exemplo.com.br).")
    if not SITE_URL.startswith('https://'):
        raise ImproperlyConfigured("Em produção SITE_URL precisa começar com https:// (ex: https://exemplo.com.br).")


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',

    'tenants',
    'vehicles',
    'storefront',
    'dashboard',
    'leads',
    'financing',
    'billing',
    'landing',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if not DEBUG:
    # Serve os arquivos estáticos (CSS/JS) pelo próprio app, comprimidos e com cache longo.
    # As fotos enviadas (media) ficam por conta do nginx: ver deploy/nginx.conf.
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

ROOT_URLCONF = 'projgaragem.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'projgaragem.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
# Sem DATABASE_URL usa SQLite (desenvolvimento). Em produção:
# DATABASE_URL=postgres://usuario:senha@localhost:5432/projgaragem

DATABASES = {
    'default': env.db('DATABASE_URL', default=f'sqlite:///{BASE_DIR / "db.sqlite3"}'),
}
if DATABASES['default']['ENGINE'].endswith('postgresql'):
    DATABASES['default']['CONN_MAX_AGE'] = env.int('DB_CONN_MAX_AGE', default=60)
    DATABASES['default']['CONN_HEALTH_CHECKS'] = True


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'  # destino do collectstatic

STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {
        'BACKEND': (
            'django.contrib.staticfiles.storage.StaticFilesStorage' if DEBUG
            else 'whitenoise.storage.CompressedManifestStaticFilesStorage'
        ),
    },
}
# Se algum arquivo faltar no manifesto, usa o caminho sem hash em vez de derrubar a página.
WHITENOISE_MANIFEST_STRICT = False

# Media files (fotos de veículos)
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Fotos de veículos: limite de upload e otimização (ver vehicles/imagens.py).
# O nginx precisa aceitar corpo maior que FOTO_UPLOAD_MAX_BYTES (client_max_body_size, ver deploy/nginx.conf).
FOTO_UPLOAD_MAX_BYTES = 15 * 1024 * 1024
FOTO_MAX_PIXELS = 50_000_000
FOTO_LADO_MAXIMO = 1280
FOTO_QUALIDADE_JPEG = 80

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Login/logout do painel da garagem
LOGIN_URL = 'dashboard:login'
LOGIN_REDIRECT_URL = 'dashboard:home'
LOGOUT_REDIRECT_URL = 'dashboard:login'


# Mercado Pago / billing
MERCADOPAGO_ACCESS_TOKEN = env('MERCADOPAGO_ACCESS_TOKEN', default='')
MERCADOPAGO_WEBHOOK_SECRET = env('MERCADOPAGO_WEBHOOK_SECRET', default='')
PLATFORM_ADMIN_EMAIL = env('PLATFORM_ADMIN_EMAIL')
DIAS_ATRASO_PARA_AVISO_ADMIN = env.int('DIAS_ATRASO_PARA_AVISO_ADMIN', default=5)
PLANO_MENSALIDADE_PADRAO = env('PLANO_MENSALIDADE_PADRAO', default='99.90')

# Usada no simulador só se a garagem não informar taxa e o Banco Central nunca tiver sido consultado
TAXA_JUROS_ESTIMADA = Decimal('2.00')

# Identificação da plataforma nos textos legais (termos de uso e privacidade)
PLATAFORMA_NOME = env('PLATAFORMA_NOME', default='projgaragem')
PLATAFORMA_CNPJ = env('PLATAFORMA_CNPJ', default='')

# Landing page (raiz do site): WhatsApp dos sócios (só dígitos com DDI, ex: 5517999999999; em
# branco, o botão da landing leva ao formulário) e a garagem cuja vitrine aparece no celular.
PLATAFORMA_WHATSAPP = re.sub(r'\D', '', env('PLATAFORMA_WHATSAPP', default=''))
PLATAFORMA_WHATSAPP_2 = re.sub(r'\D', '', env('PLATAFORMA_WHATSAPP_2', default=''))
PLATAFORMA_INSTAGRAM = env('PLATAFORMA_INSTAGRAM', default='')
LANDING_DEMO_SLUG = env('LANDING_DEMO_SLUG', default='motos-do-joao')
LANDING_DEMO_SLUG_2 = env('LANDING_DEMO_SLUG_2', default='central-motors-demo')

# A vitrine de demonstração aparece dentro de um iframe da própria landing (mesma origem).
X_FRAME_OPTIONS = 'SAMEORIGIN'


# E-mail
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='contato@projgaragem.local')
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = env('EMAIL_HOST')
    EMAIL_PORT = env.int('EMAIL_PORT', default=587)
    EMAIL_HOST_USER = env('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
    # Porta 587 usa STARTTLS (padrão); porta 465 usa SSL direto (EMAIL_USE_SSL=True).
    EMAIL_USE_SSL = env.bool('EMAIL_USE_SSL', default=False)
    EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=not EMAIL_USE_SSL)
    EMAIL_TIMEOUT = 10  # um SMTP lento não pode travar o atendimento
    DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')

SERVER_EMAIL = DEFAULT_FROM_EMAIL
ADMINS = [('Administrador', PLATFORM_ADMIN_EMAIL)]


# Segurança (só em produção)
if not DEBUG:
    # O nginx termina o HTTPS e avisa o app pelo cabeçalho X-Forwarded-Proto.
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[SITE_URL])
    # HSTS começa com 1 hora e só deve subir (31536000 = 1 ano) depois de o HTTPS estar validado:
    # o navegador obedece pelo prazo inteiro, e voltar atrás não é possível.
    SECURE_HSTS_SECONDS = env.int('SECURE_HSTS_SECONDS', default=3600)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=False)


# Logs: tudo para a saída padrão (o systemd guarda em journalctl) e e-mail ao administrador em erros 500.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'somente_producao': {'()': 'django.utils.log.RequireDebugFalse'},
    },
    'formatters': {
        'simples': {'format': '%(asctime)s %(levelname)s %(name)s: %(message)s'},
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'simples'},
        'nulo': {'class': 'logging.NullHandler'},
        'email_admins': {
            'class': 'django.utils.log.AdminEmailHandler',
            'level': 'ERROR',
            'filters': ['somente_producao'],
        },
    },
    'root': {'handlers': ['console'], 'level': 'INFO'},
    'loggers': {
        'django.request': {'handlers': ['console', 'email_admins'], 'level': 'ERROR', 'propagate': False},
        # Robôs que testam hosts aleatórios geram esse erro o dia todo; não vale e-mail nem log.
        'django.security.DisallowedHost': {'handlers': ['nulo'], 'propagate': False},
    },
}


# Sentry: captura erro 500 (com stack trace, usuário e request) e log de nível ERROR.
# Opcional — em branco, não faz nada (nenhuma chamada de rede, nem em produção).
# Crie um projeto Django gratuito em sentry.io e cole a DSN dele no .env como SENTRY_DSN.
SENTRY_DSN = env('SENTRY_DSN', default='')
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            LoggingIntegration(level=None, event_level='ERROR'),
        ],
        environment=env('SENTRY_ENVIRONMENT', default='development' if DEBUG else 'production'),
        traces_sample_rate=env.float('SENTRY_TRACES_SAMPLE_RATE', default=0.0),
        send_default_pii=False,  # dados de veículo/proposta são de terceiros (LGPD); não envia dados pessoais
    )
