"""
[_] Post
[_] Get
[_] Josnify
[_] Object creation
"""
import os

import urllib3


class APIClient:
    """Connect to the GitHub API"""

    def __init__(self, num_pools: int = 10) -> None:
        """Personal Auth Token needs to be in 'GITHUB_AUTH_TOKEN` env variable"""
        self.apiclient = urllib3.PoolManager(num_pools=num_pools)
        self._auth_token = os.getenv("GITHUB_AUTH_TOKEN", "")

        if not self._auth_token:
            raise ValueError("Missing GITHUB_AUTH_TOKEN environment variable")
