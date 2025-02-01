"""Tests."""

from collections.abc import Iterable

from django.apps import AppConfig, apps


def get_local_app_configs() -> Iterable[AppConfig]:
    """Get local Django app configs."""
    for app_config in apps.get_app_configs():
        if "site-packages" not in app_config.path:
            yield app_config
