"""Celery initialization."""

import os
from logging.config import dictConfig
from typing import Any

import celery
import dotenv
from celery.signals import setup_logging

dotenv.load_dotenv(verbose=True)


# Set up handler to configure logging.
@setup_logging.connect
def config_loggers(*args: Any, **kwargs: Any) -> None:
    """Configure loggers in Celery using Django settings."""
    from django.conf import settings

    dictConfig(settings.LOGGING)


def monkeypatch() -> None:
    """
    Monkey patch Celery tasks so type stubs don't cause issues.

    https://github.com/sbdchd/celery-types/issues/80#issuecomment-1146939586
    """
    celery.Task.__class_getitem__ = classmethod(  # type: ignore[attr-defined]
        lambda cls, *args, **kwargs: cls
    )


# Start Celery
# https://docs.celeryproject.org/en/stable/django/
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ollama_webhooks.settings")
app = celery.Celery("ollama_webhooks")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
