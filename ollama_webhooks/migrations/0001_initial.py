"""Ollama webhook migration."""

import django.contrib.postgres.functions
from django.db import migrations, models


class Migration(migrations.Migration):
    """Ollama webhook migration."""

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Job",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        db_default=django.contrib.postgres.functions.RandomUUID(),
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "request_method",
                    models.TextField(
                        choices=[
                            ("CONNECT", "CONNECT"),
                            ("DELETE", "DELETE"),
                            ("GET", "GET"),
                            ("HEAD", "HEAD"),
                            ("OPTIONS", "OPTIONS"),
                            ("PATCH", "PATCH"),
                            ("POST", "POST"),
                            ("PUT", "PUT"),
                            ("TRACE", "TRACE"),
                        ]
                    ),
                ),
                ("request_path", models.TextField(blank=True)),
                ("request_query", models.TextField(blank=True)),
                ("request_headers", models.JSONField(default=dict)),
                ("request_body", models.BinaryField(blank=True)),
                ("created_timestamp", models.DateTimeField(auto_now_add=True)),
                ("request_sent_timestamp", models.DateTimeField(blank=True, null=True)),
                (
                    "response_received_timestamp",
                    models.DateTimeField(blank=True, null=True),
                ),
                ("response_content", models.BinaryField(blank=True)),
                ("response_headers", models.JSONField(default=dict)),
            ],
        ),
    ]
