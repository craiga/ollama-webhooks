"""Views."""

import logging
from http import HTTPStatus
from typing import Any
from urllib.parse import urlencode

from django import http, urls
from django.conf import settings
from django.http import HttpResponse
from django.views.generic import DetailView, View

from ollama_webhooks import models, tasks

logger = logging.getLogger(__name__)


def response_from_status(status: HTTPStatus) -> http.HttpResponse:  # noqa: D103
    return HttpResponse(status.description, status=status)


def job_to_dict(job: models.Job, request: http.HttpRequest) -> dict[str, Any]:
    """Convert a job to a dict."""
    job_url = request.build_absolute_uri(urls.reverse("job", args=(job.pk,)))
    webhook_url = settings.WEBHOOK_URL + urlencode({"job": job.id})
    return {
        "job": str(job.pk),
        "url": job_url,
        "webhook": webhook_url,
        "created_at": str(job.created_timestamp),
        "message": (
            "You have sent a request to Ollama webhooks. Your request has entered a"
            f" queue. Once it has been processed, an HTTP {settings.WEBHOOK_METHOD}"
            f" request will be sent to {webhook_url} with Ollama's response in that"
            f" request's body. You can check these details again by visiting {job_url}."
            "\n"
            "\n"
            "I've sent the job ID in this JSON response, but have also included it"
            " below just in case you need to parse it from this message."
            "\n"
            "\n"
            f"{job.pk}"
        ),
    }


class CreateJobView(View):
    """Create job to pass on to Ollama."""

    def dispatch(
        self, request: http.HttpRequest, *args: Any, **kwargs: Any
    ) -> http.HttpResponse:
        """Create an Ollama job from this request.

        Also, simulate an Ollama response to this request so that this can be used with
        existing Ollama clients.
        """
        if not request.method:
            msg = "Request doesn't have a method, unable to create job."
            raise AssertionError(msg)

        job = models.Job.objects.create(
            request_method=request.method,
            request_path=request.path,
            request_query=request.GET.urlencode(),
            request_headers=dict(request.headers),
            request_body=request.body,
        )
        tasks.run_job.delay(job.pk)

        # Send job details, along with a minimal simulation of a request to this
        # endpoint.
        job_details = job_to_dict(job, request)
        match job.request_path:
            case "/api/ps":
                return http.JsonResponse({
                    "models": [],
                    **job_details,
                })

            case "/api/generate":
                return http.JsonResponse({
                    "response": job_details["message"],
                    **job_details,
                })

            case "/":
                return http.JsonResponse(job_details)

        logger.warning(
            (
                "Not simulating a minimal Ollama response to a request to %s. If you're"
                " able, please submit a pull request to add a minimal simulation."
            ),
            job.request_path,
        )
        return http.JsonResponse(job_details)


class JobView(DetailView[models.Job]):
    """View details of a job."""

    model = models.Job

    def render_to_response(self, *args: Any, **kwargs: Any) -> http.HttpResponse:
        """Show details of this job.

        Note that this response needs to be Ollama-like to work with Ollama clients.
        """
        return http.JsonResponse(job_to_dict(self.object, self.request))
