"""
[_] Post
[_] Get
[_] Josnify
[_] Object creation
"""
import os
from typing import Any
from typing import Dict

import urllib3


class APIClient:
    """Connect to the GitHub API"""

    def __init__(self, num_pools: int = 10) -> None:
        """Personal Auth Token needs to be in 'GITHUB_AUTH_TOKEN` env variable"""
        self.apiclient = urllib3.PoolManager(num_pools=num_pools)
        _auth_token = os.getenv("GITHUB_AUTH_TOKEN", "")
        _user_name = os.getenv("GITHUB_USER_NAME", "")

        if not _auth_token:
            raise ValueError("Missing GITHUB_AUTH_TOKEN environment variable")

        if not _user_name:
            raise ValueError("Missing GITHUB_USER_NAME environment variable")

        self.__headers = {
            "Accept": "application.vnd.github.v3+json",
            "User-Agent": _user_name,
            "Authorization": f"token {_auth_token}",
        }

    def git_get(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handles all GET requests to GitHub"""
        return {}
