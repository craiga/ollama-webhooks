"""Test that apps are installed."""

from django.apps import AppConfig
from django.conf import settings

import pytest

from ollama_webhooks.tests import get_local_app_configs


@pytest.mark.parametrize("app_config", get_local_app_configs())
def test_app_logging_configurable(app_config: AppConfig) -> None:
    """Test that app logging is configurable."""
    assert app_config.name in settings.LOGGING["loggers"]
