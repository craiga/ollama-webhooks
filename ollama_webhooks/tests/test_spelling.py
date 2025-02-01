"""Test spelling of user-visible strings in models."""

from collections.abc import Iterable
from contextlib import suppress
from typing import Any

from django.db import models
from django.utils.html import strip_tags
from django.utils.safestring import SafeString

import enchant
import pytest
from enchant.tokenize import get_tokenizer

from ollama_webhooks.tests import get_local_app_configs


@pytest.fixture(scope="session")
def dictionary() -> enchant.DictWithPWL:
    """Enchant dictionary."""
    return enchant.DictWithPWL("en_US", ".dictionary")


@pytest.fixture(scope="session")
def tokenizer() -> enchant.tokenize.Filter:
    """Get tokenizer."""
    return get_tokenizer("en_US")


def get_models() -> Iterable[type[models.Model]]:
    """Get all models."""
    for app_config in get_local_app_configs():
        yield from app_config.get_models()


def get_fields() -> Iterable[models.Field[Any, Any]]:
    """Get all fields."""
    for model in get_models():
        for field in model._meta.get_fields():
            if isinstance(field, models.Field):
                yield field


IGNORED_WORDS: Iterable[str] = ["ptr"]


@pytest.mark.parametrize("field", get_fields())
def test_verbose_name(
    field: models.Field[Any, Any],
    dictionary: enchant.DictWithPWL,
    tokenizer: enchant.tokenize.Filter,
) -> None:
    """Test that verbose name of a field don't contain any spelling errors."""
    with suppress(AttributeError):
        for word, _ in tokenizer(field.verbose_name):
            if word not in IGNORED_WORDS:
                assert dictionary.check(word), (
                    f"{word} in verbose name of {field} is misspelled (or missing"
                    " from the dictionary) "
                )


@pytest.mark.parametrize("field", get_fields())
def test_help_text(
    field: models.Field[Any, Any],
    dictionary: enchant.DictWithPWL,
    tokenizer: enchant.tokenize.Filter,
) -> None:
    """Test that help text of a field don't contain any spelling errors."""
    with suppress(AttributeError):
        text = field.help_text
        if isinstance(text, SafeString):
            text = strip_tags(text)

        for word, _ in tokenizer(text):
            if word not in IGNORED_WORDS:
                assert dictionary.check(word), (
                    f"{word} in help text of {field} is misspelled (or missing"
                    " from the dictionary) "
                )
