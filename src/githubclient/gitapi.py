# -*- coding: utf-8 -*-
""" Abstract layer for git API communication

This class gives the methods needed to accomplish the following:
    - Create a new branch in target repo from source branch
    - Upload a template file to the branch
    - Commit the file to the new branch
    - Create a pull request for new branch to source branch
    - Add labels to the pull request

Since: 2021.04.02
Author: Preocts <preocts@preocts.com>
GitHub: https://github.com/Preocts/githubclient
"""
import json
import logging
import http.client
from urllib.parse import quote
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple
from typing import Optional


class GitAPI:
    """ Create a new branch, update a file, and submit a pull request against repo """

    logger: logging.Logger = logging.getLogger(__name__)

    def __init__(self, owner: str, repo: str, oauth: str) -> None:
        """
        Provide username and personal token with correct permissions

        Args:
            owner: Owner of repo, 'github.com/[OWNER]/[REPONAME]'
            repo: Name of repo, 'github.com/[OWNER]/[REPONAME]'
            oauth: Person oauth token with permissions to commit
        """
        self.headers: Dict[str, str] = {
            "Accept": "application.vnd.github.v3+json",
            "User-Agent": owner,
            "Authorization": f"token {oauth}",
        }
        self.owner = owner
        self.repo = repo
        self.client: http.client.HTTPSConnection = http.client.HTTPSConnection(
            "api.github.com"
        )

    def _git_post(self, endpoint: str, payload: Dict[str, Any]) -> Dict[Any, Any]:
        """ Private: Handles all posts to git. """

        self.client.request("POST", endpoint, json.dumps(payload), self.headers)

        return self._handle_response()

    def _git_get(self, endpoint: str) -> Dict[Any, Any]:
        """ Private: Handles all GET to github. """

        self.client.request("GET", endpoint, None, self.headers)

        return self._handle_response()

    def _handle_response(self) -> Dict[Any, Any]:
        """ Captures errors in HTTPS request or returns valid response """
        try:
            response = self.client.getresponse()
        except http.client.ResponseNotReady as err:
            self.logger.error("No response? '%s'", err)
            return {}

        status = response.status
        raw_response = response.read().decode("utf-8")

        try:
            result = json.loads(raw_response)
        except json.JSONDecodeError as err:
            self.logger.error("Error decoding JSON response: %s", err)
            self.logger.debug("Raw response %s", raw_response)
            return {}

        if status not in range(200, 299):
            # NOTE (preocts) Could do a retry recursive call here if desired
            self.logger.error("HTTPS Response '%d', '%s'", status, result)

        return result

    def get_branch_sha(self, branch_name: str) -> str:
        """ Get the SHA of the base branch """
        # https://docs.github.com/en/rest/reference/repos#get-a-branch

        self.logger.debug("Requesting branch SHA")
        endpoint = f"/repos/{self.owner}/{self.repo}/branches/{branch_name}"

        result = self._git_get(endpoint)

        sha = result.get("commit", {}).get("sha", "")
        if not sha:
            self.logger.error("Get SHA failed: %s", result)

        return sha

    def create_branch(self, base_branch: str, new_branch: str) -> str:
        """ Creates branch from base branch, return SHA of new branch """
        # https://docs.github.com/en/rest/reference/git#create-a-reference

        self.logger.debug("Creating Branch")
        endpoint = f"/repos/{self.owner}/{self.repo}/git/refs"
        payload = {
            "ref": f"refs/heads/{new_branch}",
            "sha": self.get_branch_sha(base_branch),
        }
        result = self._git_post(endpoint, payload)
        if "message" in result and result["message"] == "Reference already exists":
            # Branch exists, recover existing SHA
            return self.get_branch_sha(new_branch)

        return result.get("object", {}).get("sha", "")

    def create_blob(self, file_contents: str) -> str:
        """ Create blob of the file_contents, returns SHA reference """
        # https://docs.github.com/en/rest/reference/git#create-a-blob

        self.logger.debug("Creating Blob")
        endpoint = f"/repos/{self.owner}/{self.repo}/git/blobs"
        payload = {
            "owner": self.owner,
            "repo": self.repo,
            "content": file_contents,
            "encoding": "utf-8",
        }

        return self._git_post(endpoint, payload).get("sha", "")

    def create_blob_tree(self, branch_sha: str, blobs: List[Tuple[str, str]]) -> str:
        """
        Create a tree link to blob(s), returns tree sha for commit

        Args:
            branch_sha: Target branch sha
            blobls: List of (blob_sha, file_path) tuples
        """
        # https://docs.github.com/en/rest/reference/git#create-a-tree

        self.logger.debug("Creating Tree")
        endpoint = f"/repos/{self.owner}/{self.repo}/git/trees"
        trees: List[Dict[str, str]] = []

        for blob_sha, file_path in blobs:
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
        return self._git_post(endpoint, payload).get("sha", "")

    def create_commit(
        self, author_name: str, author_email: str, branch_sha: str, tree_sha: str
    ) -> str:
        """ Creates commit to branch """
        # https://docs.github.com/en/rest/reference/git#create-a-commit

        self.logger.debug("Create commit")
        endpoint = f"/repos/{self.owner}/{self.repo}/git/commits"
        payload = {
            "message": "Auto commit by AIM Orc WatchTower",
            "author": {
                "name": author_name,
                "email": author_email,
            },
            "parents": [branch_sha],
            "tree": tree_sha,
        }

        return self._git_post(endpoint, payload).get("sha", "")

    def update_reference(self, branch_name: str, commit_sha: str) -> str:
        """ Create or update the reference of a branch """
        # https://docs.github.com/en/rest/reference/git#update-a-reference

        self.logger.debug("Update branch ref")
        endpoint = f"/repos/{self.owner}/{self.repo}/git/refs/heads/{branch_name}"
        payload = {
            "ref": f"refs/heads/{branch_name}",
            "sha": commit_sha,
        }

        return self._git_post(endpoint, payload).get("object", {}).get("sha", "")

    def create_pull_request(
        self, base_branch: str, head_branch: str, pr_title: str, pr_body: str
    ) -> Optional[int]:
        """ Create PR from head_branch -> base_branch """
        # https://docs.github.com/en/rest/reference/pulls#create-a-pull-request

        self.logger.debug("Create pull request")
        endpoint = f"/repos/{self.owner}/{self.repo}/pulls"
        payload = {
            "owner": self.owner,
            "repo": self.repo,
            "title": pr_title,
            "head": head_branch,
            "base": base_branch,
            "body": pr_body,
            "maintainer_can_modify": True,
        }

        number = self._git_post(endpoint, payload).get("number")

        return number if number else self.recover_pull_request(head_branch)

    def recover_pull_request(self, head_branch: str) -> Optional[int]:
        """ Attempts to find existing PR by branch name, fails if more/less than 1 """
        # https://docs.github.com/en/rest/reference/issues#list-repository-issues
        params = quote(f"head={head_branch}")
        endpoint = f"/repos/{self.owner}/{self.repo}/pulls?{params}"

        result = self._git_get(endpoint)

        if not isinstance(result, list) or len(result) > 1:
            self.logger.warning("Unable to find exact PR for '%s'", head_branch)
            return None

        return result[0].get("number") if result else None

    def add_lables(self, number: int, labels: List[str]) -> None:
        """ Add labels to a pull request """
        # https://docs.github.com/en/rest/reference/issues#add-labels-to-an-issue

        self.logger.debug("Add labels")
        endpoint = f"/repos/{self.owner}/{self.repo}/issues/{number}/labels"
        payload = {
            "labels": labels,
        }

        if labels:
            self._git_post(endpoint, payload)
