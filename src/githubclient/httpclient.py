"""
Abstract base HTTPS API actions against GitHub (CRUD operations)

Author: Preocts <Preocts#8196>
"""
from __future__ import annotations

import json
import logging
import os
from http import client
from typing import Any


class HTTPClient:
    """Connect to the GitHub API"""

    host = "https://api.github.com"

    logger = logging.getLogger("APIClient")

    def __init__(self, host: str | None = None) -> None:
        """
        Environment variables are required for authentication.

        GITHUB_AUTH_TOKEN: GitHub personal access token
        GITHUB_USER_NAME: GitHub username

        Args:
            host: GitHub API host, defaults to https://api.github.com
        """
        self._validate_environs()
        self.headers = {
            "Accept": "application.vnd.github.v3+json",
            "User-Agent": os.environ["GITHUB_USER_NAME"],
            "Authorization": f"token {os.environ['GITHUB_AUTH_TOKEN']}",
        }
        self.apiclient = client.HTTPSConnection(self._clean_host(host), timeout=15)

    def _clean_host(self, host: str | None) -> str:
        """Remove the leading protocol from the host and trailing slash"""
        host = host or self.host
        return self.host.replace("https://", "").replace("/", "")

    def _validate_environs(self) -> None:
        """Check for required environment variables, raise error if missing."""
        missing_token_msg = "Missing GITHUB_AUTH_TOKEN environment variable"
        missing_username_msg = "Missing GITHUB_USER_NAME environment variable"

        msg = [] if os.getenv("GITHUB_AUTH_TOKEN", "") else [missing_token_msg]
        msg.extend([] if os.getenv("GITHUB_USER_NAME", "") else [missing_username_msg])

        if msg:
            raise OSError(", ".join(msg))

    def git_get(self, endpoint: str) -> dict[str, Any]:
        """Handles all GET requests to GitHub"""

        self.apiclient.request(
            method="GET",
            url=endpoint,
            headers=self.headers,
        )
        response = self.apiclient.getresponse()
        status_code = response.status
        result = response.read()

        if status_code not in range(200, 299):
            self.logger.error("%s - %s", endpoint, result)

        return self._jsonify(result)

    def git_post(self, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Handles all POST requests to GitHub, payload is translated to body"""

        self.apiclient.request(
            method="POST",
            url=endpoint,
            body=json.dumps(payload),
            headers=self.headers,
        )
        response = self.apiclient.getresponse()
        status_code = response.status
        result = response.read()

        if status_code not in range(200, 299):
            self.logger.error("%s - %s", endpoint, result)

        return self._jsonify(result)

    @staticmethod
    def _jsonify(data: bytes) -> dict[str, Any]:
        """Translate response bytes to dict, returns key 'error' if failed"""
        try:
            return json.loads(data.decode("utf-8"))
        except json.JSONDecodeError:
            return {"error": data}
