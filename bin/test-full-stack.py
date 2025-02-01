#!/usr/bin/env python3
"""Test a running full stack."""

from http.server import BaseHTTPRequestHandler, HTTPServer
from socket import socket
from typing import Any
from urllib.parse import parse_qs, urlparse

import requests


class WebhookJobListener(HTTPServer):
    """Listen for webhook requests."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """OAuth HTTP server."""
        super().__init__(*args, **kwargs)
        self.last_path: str | None = None

    def next_job(self) -> str:
        """Wait for an HTTP request, which will contain a job ID."""
        self.handle_request()
        return parse_qs(str(urlparse(self.last_path).query))["job"][0]


class WebhookRequestHandler(BaseHTTPRequestHandler):
    """Handle webhook requests."""

    def __init__(
        self,
        request: socket,
        client_address: tuple[str, int],
        server: WebhookJobListener,
    ) -> None:
        """HTTP request handler for OAuth listening."""
        super().__init__(request, client_address, server)
        server.last_path = self.path

    def do_POST(self) -> None:  # noqa: N802
        """Send response to POST request."""
        body = bytes("Thank you!", "utf-8")
        self.protocol_version = "HTTP/1.1"
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    """Test a running full stack."""
    response = requests.post(
        "http://localhost:11435/api/generate",
        json={"model": "llama3.2", "prompt": "Tell me a joke."},
        timeout=10,
    )
    response.raise_for_status()
    expected_job = response.json()["job"]

    with WebhookJobListener(("localhost", 11436), WebhookRequestHandler) as server:
        while server.next_job() != expected_job:
            pass


if __name__ == "__main__":
    main()
