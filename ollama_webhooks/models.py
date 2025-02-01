"""Ollama webhook models."""

import http

from django.contrib.postgres.functions import RandomUUID
from django.db import models


class Job(models.Model):
    """An Ollama job."""

    id = models.UUIDField(db_default=RandomUUID(), editable=False, primary_key=True)
    request_method = models.TextField(
        null=False,
        blank=False,
        choices=[(method.name, method.value) for method in http.HTTPMethod],
    )
    request_path = models.TextField(null=False, blank=True)
    request_query = models.TextField(null=False, blank=True)
    request_headers = models.JSONField(null=False, blank=False, default=dict)
    request_body = models.BinaryField(null=False, blank=True)
    created_timestamp = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    request_sent_timestamp = models.DateTimeField(null=True, blank=True)
    response_received_timestamp = models.DateTimeField(null=True, blank=True)
    response_content = models.BinaryField(null=False, blank=True)
    response_headers = models.JSONField(null=False, blank=False, default=dict)

    def __str__(self) -> str:
        """User-friendly representation of this job."""
        return str(self.id)
