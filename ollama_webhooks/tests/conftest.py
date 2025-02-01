"""Globally available test fixtures."""

import logging
import os
from collections.abc import Generator
from unittest import mock

from django.test.utils import override_settings

import pytest

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session", autouse=True)
def _set_settings() -> Generator[None, None, None]:
    """Global settings for all tests."""
    with override_settings(CELERY_BROKER="memory://", DEBUG=False):
        yield


@pytest.fixture(scope="session", autouse=True)
def _set_environment_variables() -> Generator[None, None, None]:
    """Override global environment variables in all tests."""
    with mock.patch.dict(os.environ, {}):
        yield
