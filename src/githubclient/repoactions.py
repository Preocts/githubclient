"""
GitHub Actions for Repos

Author: Preocts (Preocts#8196)
"""
from __future__ import annotations

import logging
from typing import Any
from typing import NamedTuple

from githubclient.httpclient import HTTPClient


class RepoReturn(NamedTuple):
    """Return values from Repo actions"""

    full_return: dict[str, Any] = {}
    sha: str = ""
    url: str = ""
    html_url: str = ""


class RepoActions:
    """Actions for repos in GitHub"""

    logger = logging.getLogger(__name__)

    def __init__(self, repo_owner: str, repo_name: str) -> None:
        """Create client class. num_pools = https pool manager"""
        self.http_client = HTTPClient()
        self.repo = repo_name
        self.owner = repo_owner

    def get_branch(self, branch_name: str) -> RepoReturn:
        """Get a branch"""
        # https://docs.github.com/en/rest/reference/repos#get-a-branch

        self.logger.debug("Requesting SHA of branch: %s", branch_name)
        endpoint = f"/repos/{self.owner}/{self.repo}/branches/{branch_name}"

        result = self.http_client.git_get(endpoint)

        return RepoReturn(
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

        result = self.http_client.git_post(endpoint, payload)

        return RepoReturn(
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

        result = self.http_client.git_post(endpoint, payload)

        return RepoReturn(
            full_return=result,
            sha=result.get("sha", ""),
        )

    def create_blob_tree(
        self, branch_sha: str, blob_names: list[tuple[str, str]]
    ) -> RepoReturn:
        """
        Link blob(s) to a tree at the branch provided

        Args:
            branch_sha: SHA of branch to create tree
            blob_names: List of ([blob SHA], [filename])
        """
        # https://docs.github.com/en/rest/reference/git#create-a-tree

        self.logger.debug("Creating Tree")

        endpoint = f"/repos/{self.owner}/{self.repo}/git/trees"
        trees: list[dict[str, str]] = []

        for blob_sha, file_path in blob_names:
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

        result = self.http_client.git_post(endpoint, payload)

        return RepoReturn(
            full_return=result,
            sha=result.get("sha", ""),
            url=result.get("url", ""),
        )

    def create_commit(
        self,
        author_name: str,
        author_email: str,
        branch_sha: str,
        tree_sha: str,
        message: str = "Auto commit",
    ) -> RepoReturn:
        """Creates commit to branch"""
        # https://docs.github.com/en/rest/reference/git#create-a-commit

        self.logger.debug("Create commit of %s to %s", tree_sha, branch_sha)
        endpoint = f"/repos/{self.owner}/{self.repo}/git/commits"
        payload = {
            "message": message,
            "author": {
                "name": author_name,
                "email": author_email,
            },
            "parents": [branch_sha],
            "tree": tree_sha,
        }

        result = self.http_client.git_post(endpoint, payload)

        return RepoReturn(
            full_return=result,
            sha=result.get("sha", ""),
            url=result.get("url", ""),
            html_url=result.get("html_url", ""),
        )

    def update_reference(self, branch_name: str, commit_sha: str) -> RepoReturn:
        """Create or update the reference of a branch"""
        # https://docs.github.com/en/rest/reference/git#update-a-reference

        self.logger.debug("Update branch %s to ref %s", branch_name, commit_sha)
        endpoint = f"/repos/{self.owner}/{self.repo}/git/refs/heads/{branch_name}"
        payload = {
            "ref": f"refs/heads/{branch_name}",
            "sha": commit_sha,
        }

        result = self.http_client.git_post(endpoint, payload)

        return RepoReturn(
            full_return=result,
            sha=result.get("object", {}).get("sha", ""),
            url=result.get("object", {}).get("url", ""),
        )

    def create_pull_request(
        self,
        new_branch: str,
        base_branch: str,
        pr_title: str = "Auto PR",
        pr_body: str = "PR Auto Generated",
        draft: bool = False,
    ) -> RepoReturn:
        """Create PR of new_branch merging into base_branch"""
        # https://docs.github.com/en/rest/reference/pulls#create-a-pull-request

        self.logger.debug("Create pull request of %s to %s", new_branch, base_branch)
        endpoint = f"/repos/{self.owner}/{self.repo}/pulls"
        payload = {
            "owner": self.owner,
            "repo": self.repo,
            "title": pr_title,
            "head": new_branch,
            "base": base_branch,
            "body": pr_body,
            "maintainer_can_modify": True,
            "draft": draft,
        }

        result = self.http_client.git_post(endpoint, payload)

        return RepoReturn(
            full_return=result,
            sha=str(result.get("number", "")),
            url=result.get("url", ""),
            html_url=result.get("html_url", ""),
        )

    def add_labels(self, number: str, labels: list[str]) -> RepoReturn:
        """Add label(s) to an existing pull request"""
        # https://docs.github.com/en/rest/reference/issues#add-labels-to-an-issue

        self.logger.debug("Add labels")
        endpoint = f"/repos/{self.owner}/{self.repo}/issues/{number}/labels"
        payload = {
            "labels": labels,
        }

        result = self.http_client.git_post(endpoint, payload)

        return RepoReturn(
            full_return=result,
        )
