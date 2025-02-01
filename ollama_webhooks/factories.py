"""Object factories."""

import logging

from django.conf import settings

from ollama import Client as OllamaClient

logger = logging.getLogger(__name__)


def ollama() -> OllamaClient:
    """Get Ollama client."""
    return OllamaClient(host=settings.OLLAMA_URL)
