"""
Abstract base API actions against GitHub (CRUD operations)

Author: Preocts <Preocts#8196>
"""
import json
import logging
import os
from typing import Any
from typing import Dict

import urllib3
from githubclient.apimetrics import capmetrics


class APIClient:
    """Connect to the GitHub API"""

    BASE_URL = "https://api.github.com"

    logger = logging.getLogger("APIClient")

    def __init__(self, num_pools: int = 10) -> None:
        """Personal Auth Token needs to be in 'GITHUB_AUTH_TOKEN` env variable"""
        auth_token = os.getenv("GITHUB_AUTH_TOKEN", "")
        user_name = os.getenv("GITHUB_USER_NAME", "")
        headers = {
            "Accept": "application.vnd.github.v3+json",
            "User-Agent": user_name,
            "Authorization": f"token {auth_token}",
        }

        if not auth_token:
            self.logger.warning("Missing GITHUB_AUTH_TOKEN environment variable")

        if not user_name:
            self.logger.warning("Missing GITHUB_USER_NAME environment variable")

        self.apiclient = urllib3.PoolManager(
            num_pools=num_pools,
            headers=headers,
            retries=urllib3.Retry(total=3, backoff_factor=2),
        )

    @capmetrics
    def git_get(self, endpoint: str) -> Dict[str, Any]:
        """Handles all GET requests to GitHub"""

        result = self.apiclient.request(
            method="GET",
            url=self.BASE_URL + endpoint,
        )

        return self._jsonify(result.data)

    @capmetrics
    def git_post(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handles all POST requests to GitHub, payload is translated to body"""

        result = self.apiclient.request(
            method="POST",
            url=self.BASE_URL + endpoint,
            body=json.dumps(payload),
        )

        return self._jsonify(result.data)

    @staticmethod
    def _jsonify(data: bytes) -> Dict[str, Any]:
        """Translate response bytes to dict, returns key 'error' if failed"""
        try:
            return json.loads(data.decode("utf-8"))
        except json.JSONDecodeError:
            return {"error": data}
