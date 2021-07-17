"""
GitHub Actions for Repos

Author: Preocts (Preocts#8196)
"""
from typing import Any
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Tuple

from githubclient.apiclient import APIClient


class RepoActions(APIClient):
    """Actions for repos in GitHub"""

    class RepoReturn(NamedTuple):
        """Return values from Repo actions"""

        full_return: Dict[str, Any] = {}
        sha: str = ""
        url: str = ""
        html_url: str = ""

    def __init__(self, repo_owner: str, repo_name: str, num_pools: int = 10) -> None:
        """Create client class. num_pools = https pool manager"""
        super().__init__(num_pools=num_pools)
        self.repo = repo_name
        self.owner = repo_owner

    def get_branch(self, branch_name: str) -> RepoReturn:
        """Get a branch"""
        # https://docs.github.com/en/rest/reference/repos#get-a-branch

        self.logger.debug("Requesting SHA of branch: %s", branch_name)
        endpoint = f"/repos/{self.owner}/{self.repo}/branches/{branch_name}"

        result = self.git_get(endpoint)

        return self.RepoReturn(
            full_return=result,
            sha=result.get("commit", {}).get("sha", ""),
            url=result.get("url", ""),
            html_url=result.get("html_url", ""),
        )

    def create_branch(self, base_branch: str, new_branch: str) -> RepoReturn:
        """Creates branch from base branch"""
        # https://docs.github.com/en/rest/reference/git#create-a-reference

        self.logger.debug("Creating '%s' from '%s'", new_branch, base_branch)
        endpoint = f"/repos/{self.owner}/{self.repo}/git/refs"
        payload = {
            "ref": f"refs/heads/{new_branch}",
            "sha": self.get_branch(base_branch).sha,
        }

        result = self.git_post(endpoint, payload)

        return self.RepoReturn(
            full_return=result,
            sha=result.get("object", {}).get("sha", ""),
            url=result.get("object", {}).get("url", ""),
        )

    def create_blob(self, file_contents: str) -> RepoReturn:
        """Creates utf-8 blob of the file_contents"""
        # https://docs.github.com/en/rest/reference/git#create-a-blob

        self.logger.debug("Creating blob")
        endpoint = f"/repos/{self.owner}/{self.repo}/git/blobs"
        payload = {
            "owner": self.owner,
            "repo": self.repo,
            "content": file_contents,
            "encoding": "utf-8",
        }

        result = self.git_post(endpoint, payload)

        return self.RepoReturn(
            full_return=result,
            sha=result.get("sha", ""),
        )

    def create_blob_tree(
        self, branch_sha: str, blob_shas: List[Tuple[str, str]]
    ) -> RepoReturn:
        """Link blob(s) to a tree at the branch provided"""
        # https://docs.github.com/en/rest/reference/git#create-a-tree

        self.logger.debug("Creating Tree")

        endpoint = f"/repos/{self.owner}/{self.repo}/git/trees"
        trees: List[Dict[str, str]] = []

        for blob_sha, file_path in blob_shas:
            trees.append(
                {
                    "path": file_path,
                    "mode": "100644",
                    "type": "blob",
                    "sha": blob_sha,
                }
            )

        payload = {
            "base_tree": branch_sha,
            "owner": self.owner,
            "repo": self.repo,
            "tree": trees,
        }

        result = self.git_post(endpoint, payload)

        return self.RepoReturn(
            full_return=result,
            sha=result.get("sha", ""),
            url=result.get("url", ""),
        )
