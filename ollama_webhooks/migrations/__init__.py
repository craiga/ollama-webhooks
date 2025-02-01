"""Reusable field definitions to stop pylint from complaining about duplicate code."""

import uuid
from typing import Any

from django.db import models

ID_FIELD: tuple[str, models.Field[Any, Any]] = (
    "id",
    models.BigAutoField(
        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
    ),
)

UUID_ID_FIELD: tuple[str, models.Field[Any, Any]] = (
    "id",
    models.UUIDField(
        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
    ),
)

NAME_FIELD: tuple[str, models.Field[Any, Any]] = ("name", models.TextField())

UNIQUE_CODE_FIELD: tuple[str, models.Field[Any, Any]] = (
    "code",
    models.TextField(unique=True),
)

WAFFLE_NAME_FIELD: tuple[str, models.Field[Any, Any]] = (
    "name",
    models.CharField(
        help_text="The human/computer readable name.",
        max_length=100,
        unique=True,
        verbose_name="Name",
    ),
)
