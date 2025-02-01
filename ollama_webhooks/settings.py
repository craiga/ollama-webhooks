"""Settings."""

import logging
import os
from collections.abc import Iterable, Mapping
from http.client import HTTPConnection
from pathlib import Path
from typing import Any

import corsheaders.defaults
import dj_database_url
import django_stubs_ext
import sentry_sdk
from sentry_sdk.integrations import celery as sentry_celery
from sentry_sdk.integrations import django as sentry_django
from sentry_sdk.integrations import logging as sentry_logging
from sentry_sdk.integrations import redis as sentry_redis

import ollama_webhooks.celery

logger = logging.getLogger(__name__)


# Full support for Django and Celery typing stubs.
# https://github.com/typeddjango/django-stubs/tree/master/django_stubs_ext
django_stubs_ext.monkeypatch()
ollama_webhooks.celery.monkeypatch()


BASE_DIR: Path = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get("SECRET_KEY", "not-so-secret")
DEBUG = bool(os.environ.get("DEBUG"))


# Allowed Hosts
# https://docs.djangoproject.com/en/stable/ref/settings/#allowed-hosts

ALLOWED_HOSTS = ["localhost"]

if DEBUG:
    ALLOWED_HOSTS.append("*")

if "ALLOWED_HOSTS" in os.environ:
    for allowed_host in os.environ["ALLOWED_HOSTS"].split():
        ALLOWED_HOSTS.append(allowed_host)
        if allowed_host.startswith("www."):
            ALLOWED_HOSTS.append(allowed_host[4:])
        else:
            ALLOWED_HOSTS.append(f"www.{allowed_host}")

if "CANONICAL_HOST" in os.environ:
    canonical_host = os.environ["CANONICAL_HOST"]
    ALLOWED_HOSTS.append(canonical_host)
    if canonical_host.startswith("www."):
        ALLOWED_HOSTS.append(canonical_host[4:])
    else:
        ALLOWED_HOSTS.append(f"www.{canonical_host}")


# Enforce host
# https://github.com/dabapps/django-enforce-host
if not DEBUG:
    ENFORCE_HOST = os.environ.get("CANONICAL_HOST")


# Application definition

INSTALLED_APPS = [
    # First-party
    "ollama_webhooks",
    # Third-party
    "corsheaders",
    "django_linear_migrations",
    "django_rich",
    # Django
    "django.contrib.postgres",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "enforce_host.EnforceHostMiddleware",
    "csp.middleware.CSPMiddleware",
    "django_permissions_policy.PermissionsPolicyMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "ollama_webhooks.urls"


WSGI_APPLICATION = "ollama_webhooks.wsgi.application"


# Database
# https://docs.djangoproject.com/en/stable/ref/settings/#databases
# https://github.com/jacobian/dj-database-url

DATABASES = {
    "default": dj_database_url.config(
        conn_max_age=int(os.environ.get("CONN_MAX_AGE", 0)),
        conn_health_checks=bool(os.environ.get("CONN_HEALTH_CHECKS")),
    )
}


# Celery
# https://docs.celeryproject.org/en/stable/userguide/configuration.html
# https://docs.celeryproject.org/en/stable/getting-started/backends-and-brokers/redis.html

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL")
CELERY_BROKER_USE_SSL: bool | Mapping[str, int] = bool(
    os.environ.get("CELERY_BROKER_USE_SSL", True)
)
CELERY_TASK_ALWAYS_EAGER = bool(os.environ.get("CELERY_TASK_ALWAYS_EAGER", False))
CELERY_TASK_DEFAULT_QUEUE = os.environ.get("CELERY_TASK_QUEUE", "ollama_webhooks")
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_TASK_SOFT_TIME_LIMIT = int(os.environ.get("CELERY_TASK_SOFT_TIME_LIMIT", 120))
CELERY_TASK_TIME_LIMIT = int(
    os.environ.get("CELERY_TASK_TIME_LIMIT", CELERY_TASK_SOFT_TIME_LIMIT + 30)
)
CELERY_WORKER_CONCURRENCY = int(os.environ.get("CELERY_WORKER_CONCURRENCY", 1))
CELERY_WORKER_PREFETCH_MULTIPLIER = int(
    os.environ.get("CELERY_WORKER_PREFETCH_MULTIPLIER", 1)
)

# Will become the default in Celery 6.
# https://docs.celeryq.dev/en/stable/userguide/configuration.html
# #worker-cancel-long-running-tasks-on-connection-loss
CELERY_WORKER_CANCEL_LONG_RUNNING_TASKS_ON_CONNECTION_LOSS = bool(
    os.environ.get("CELERY_WORKER_CANCEL_LONG_RUNNING_TASKS_ON_CONNECTION_LOSS", True)
)


# Default primary key field type
# https://docs.djangoproject.com/en/stable/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Logging
# https://docs.djangoproject.com/en/stable/topics/logging/
# Based on Heroku's recommended logging setup
# (https://github.com/heroku/django-heroku/blob/master/django_heroku/core.py) and
# https://stackoverflow.com/a/48291899/1852024.

logging.captureWarnings(capture=True)


LOGGING: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": (
                "%(asctime)s [%(process)d] [%(levelname)s] pathname=%(pathname)s "
                "lineno=%(lineno)s funcname=%(funcName)s %(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "rich": {
            "datefmt": "[%X]",
            "format": os.environ.get("RICH_LOG_FORMAT", "%(message)s"),
        },
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "handlers": {
        "console": {
            "level": os.environ.get("CONSOLE_LOG_LEVEL", "DEBUG"),
            "class": "logging.StreamHandler",
            "formatter": os.environ.get("CONSOLE_LOG_FORMATTER", "verbose"),
        },
        "rich": {
            "level": os.environ.get("RICH_LOG_LEVEL", "DEBUG"),
            "class": "rich.logging.RichHandler",
            "formatter": "rich",
            "rich_tracebacks": os.environ.get("RICH_LOGGING_TRACEBACKS", DEBUG),
            "tracebacks_show_locals": os.environ.get(
                "RICH_LOGGING_TRACEBACKS_SHOW_LOCALS", DEBUG
            ),
        },
    },
    "root": {
        "handlers": os.environ.get("ROOT_LOG_HANDLERS", "console").split(),
        "level": os.environ.get("ROOT_LOG_LEVEL", "INFO"),
    },
    "loggers": {},
}


# Local loggers.
if isinstance(LOGGING["loggers"], dict):
    LOGGING["loggers"].update({
        logger_name: {
            "level": os.environ.get(
                logger_name.upper().replace(".", "_") + "_LOG_LEVEL",
                os.environ.get("ROOT_LOG_LEVEL", "INFO"),
            )
        }
        for logger_name in ["ollama_webhooks"]
    })


# Particularly chatty or interesting loggers we want to configure separately.
if isinstance(LOGGING["loggers"], dict):
    LOGGING["loggers"].update({
        logger_name: {
            "level": os.environ.get(
                logger_name.upper().replace(".", "_") + "_LOG_LEVEL", "INFO"
            ),
            # Some libraries configure their own handlers; disable those.
            "handlers": [],
        }
        for logger_name in [
            "asyncio",
            "celery",
            "django",
            "psycopg",
            "sentry_sdk",
            "urllib3",
        ]
    })


# Hook to set low-level HTTP debugging log level.

HTTPConnection.debuglevel = int(os.environ.get("LOW_LEVEL_HTTP_DEBUG_LEVEL", 0))


# Sentry
# https://github.com/getsentry/sentry-python

SENTRY_DSN = os.environ.get("SENTRY_DSN")
SENTRY_ENVIRONMENT = os.environ.get("SENTRY_ENVIRONMENT")
SENTRY_RELEASE: str | None = os.environ.get("SENTRY_RELEASE")
SENTRY_TRACES_SAMPLE_RATE = float(os.environ.get("SENTRY_TRACES_SAMPLE_RATE", 0))
SENTRY_TRACES_ENABLED = bool(
    os.environ.get("SENTRY_TRACES_ENABLED", SENTRY_TRACES_SAMPLE_RATE != 0.0)
)
SENTRY_PROFILES_SAMPLE_RATE = float(os.environ.get("SENTRY_PROFILES_SAMPLE_RATE", 0))
SENTRY_DEBUG = bool(os.environ.get("SENTRY_DEBUG", DEBUG))

if SENTRY_DSN:
    sentry_sdk.init(
        integrations=[
            sentry_celery.CeleryIntegration(),
            sentry_django.DjangoIntegration(),
            sentry_logging.LoggingIntegration(
                level=logging.INFO, event_level=logging.WARNING
            ),
            sentry_redis.RedisIntegration(),
        ],
        environment=SENTRY_ENVIRONMENT,
        release=SENTRY_RELEASE,
        enable_tracing=SENTRY_TRACES_ENABLED,
        traces_sample_rate=SENTRY_TRACES_SAMPLE_RATE,
        profiles_sample_rate=SENTRY_PROFILES_SAMPLE_RATE,
        debug=SENTRY_DEBUG,
    )


# Security
# https://docs.djangoproject.com/en/stable/topics/security/

SECURE_SSL_REDIRECT = bool(os.environ.get("SECURE_SSL_REDIRECT", not DEBUG))
SECURE_HSTS_SECONDS = int(
    os.environ.get(
        "SECURE_HSTS_SECONDS",
        (0 if not SECURE_SSL_REDIRECT else 2592000),  # 30 days (60 * 60 * 24 * 30)
    )
)


SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = SECURE_SSL_REDIRECT
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = SECURE_SSL_REDIRECT
CSRF_COOKIE_SECURE = SECURE_SSL_REDIRECT
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "same-origin"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# System checks
# https://docs.djangoproject.com/en/stable/ref/checks/

SILENCED_SYSTEM_CHECKS = ["security.W002", "security.W003"]

if "localhost" in ALLOWED_HOSTS:
    SILENCED_SYSTEM_CHECKS += [
        "security.W004",
        "security.W008",
        "security.W012",
        "security.W016",
    ]


# Content Security Policy
# https://django-csp.readthedocs.io/en/stable/configuration.html

CSP_DEFAULT_SRC: Iterable[str] = []
CSP_CONNECT_SRC = (
    ["'self'", "https://*.ingest.sentry.io", "https://*.ingest.us.sentry.io"]
    + [f"https://{allowed_host}" for allowed_host in ALLOWED_HOSTS]
    + [
        f"http://{allowed_host}"
        for allowed_host in ALLOWED_HOSTS
        if not SECURE_SSL_REDIRECT
    ]
)
CSP_FONT_SRC = ["'self'"]
CSP_FRAME_SRC = ["'self'"]
CSP_IMG_SRC = [
    "'self'",
    "https://*.gravatar.com",
    "https://*.wp.com",
    "data:",  # required for Firefox
]
CSP_STYLE_SRC = ["'self'"]
CSP_SCRIPT_SRC = ["'self'", "'unsafe-eval'"]
CSP_INCLUDE_NONCE_IN = ["script-src", "style-src"]
CSP_REPORT_URI = os.environ.get("CSP_REPORT_URI", None)
CSP_REPORT_ONLY = bool(os.environ.get("CSP_REPORT_ONLY", False))

# If sentry_environment is correctly set in query string, add sentry_release as well.
if CSP_REPORT_URI and f"sentry_environment={SENTRY_ENVIRONMENT}" in CSP_REPORT_URI:
    CSP_REPORT_URI = CSP_REPORT_URI.replace(
        f"sentry_environment={SENTRY_ENVIRONMENT}",
        f"sentry_environment={SENTRY_ENVIRONMENT}&sentry_release={SENTRY_RELEASE}",
    )


# Permissions policy
# https://github.com/adamchainz/django-permissions-policy#setting

PERMISSIONS_POLICY: Mapping[str, Iterable[str]] = {
    "autoplay": [],
    "camera": [],
    "clipboard-read": [],
    "clipboard-write": [],
    "cross-origin-isolated": [],
    "display-capture": [],
    "document-domain": [],
    "encrypted-media": [],
    "execution-while-not-rendered": [],
    "execution-while-out-of-viewport": [],
    "geolocation": [],
    "gyroscope": [],
    "magnetometer": [],
    "microphone": [],
    "otp-credentials": [],
    "publickey-credentials-get": [],
    "usb": [],
}


# Sessions
# https://docs.djangoproject.com/en/stable/topics/http/sessions/

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"


# Cross-Origin Resource Sharing (CORS)
# https://github.com/adamchainz/django-cors-headers

CORS_ALLOW_HEADERS = [*list(corsheaders.defaults.default_headers)]
CORS_PREFLIGHT_MAX_AGE = 0 if DEBUG else 86400


# Memory

DATA_UPLOAD_MAX_MEMORY_SIZE = int(
    os.environ.get("DATA_UPLOAD_MAX_MEMORY_SIZE", 1024 * 1024 * 10)
)


# Ollama

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_TIMEOUT = int(os.environ.get("OLLAMA_TIMEOUT", CELERY_TASK_SOFT_TIME_LIMIT))
WEBHOOK_METHOD = os.environ.get("WEBHOOK_METHOD", "POST")
WEBHOOK_URL = os.environ["WEBHOOK_URL"]
WEBHOOK_TIMEOUT = float(int(os.environ.get("WEBHOOK_TIMEOUT", 5)))
