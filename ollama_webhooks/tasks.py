"""Tasks."""

import logging
from typing import Any
from urllib.parse import urlsplit, urlunsplit
from uuid import UUID

from django.conf import settings
from django.core import management
from django.db import transaction
from django.utils import timezone

import requests

from ollama_webhooks import celery, models

logger = logging.getLogger(__name__)


@celery.app.task(ignore_result=True)
def call_command(*args: Any, **kwargs: Any) -> None:
    """Call a Django management command in a Celery task."""
    logger.info("Calling command %s", args[0])
    management.call_command(*args, **kwargs)


@celery.app.task
def run_job(pk: UUID) -> None:
    """Run a job."""
    with transaction.atomic():
        job = models.Job.objects.select_for_update().get(pk=pk)
        job.request_sent_timestamp = timezone.now()
        job.save()

    ollama_url = urlsplit(settings.OLLAMA_URL)
    ollama_response = requests.request(
        job.request_method,
        urlunsplit((
            ollama_url.scheme,
            ollama_url.netloc,
            job.request_path,
            job.request_query,
            ollama_url.fragment,
        )),
        data=job.request_body,
        headers=job.request_headers,
        timeout=settings.OLLAMA_TIMEOUT,
    )
    try:
        ollama_response.raise_for_status()
    except requests.HTTPError as exc:
        exc.add_note("Response content: " + str(ollama_response.content))

    with transaction.atomic():
        job = models.Job.objects.select_for_update().get(pk=pk)
        job.response_received_timestamp = timezone.now()
        job.response_content = ollama_response.content
        job.response_headers = dict(ollama_response.headers)
        job.save()

    webhook_response = requests.request(
        settings.WEBHOOK_METHOD,
        settings.WEBHOOK_URL,
        params={"job": str(job.pk)},
        data=job.response_content,
        timeout=settings.WEBHOOK_TIMEOUT,
    )
    try:
        webhook_response.raise_for_status()
    except requests.HTTPError as exc:
        exc.add_note("Response content: " + str(webhook_response.content))
