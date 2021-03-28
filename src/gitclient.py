# -*- coding: utf-8 -*-
""" Abstract layer for git API communication

This class gives the methods needed to accomplish the following:
    - Create a new branch in target repo from source branch
    - Upload a template file to the branch
    - Commit the file to the new branch
    - Create a pull request for new branch to source branch

Author: Preocts <preocts@preocts.com>

Usage:
    from gitclient import GitClient

    ...
    # Code to load/create template file as string, utf-8
    ...
    client = GitClient(
        name="Preocts",
        email="preocts@preocts.com",
        owner="preocts",
        repo="my_test_repo",
        oauth="[OAuth Secret],
    )
    client.send_template(
        base_branch="main",
        new_branch="my_cool_branch,
        file_name="cool_template_file.md",
        file_contents="string_of_file",
        pr_title="Pull request Title",
        pr_content="Pull request message",
    )
"""
import json
import logging
import http.client
from typing import Optional


class GitClient:
    """ Create a new branch, update a file, and submit a pull request against repo """

    logger = logging.getLogger(__name__)

    def __init__(
        self, name: str, email: str, owner: str, repo: str, oauth: str
    ) -> None:
        """
        Provide username and personal token with correct permissions

        Args:
            name: Team member name signing the commit
            email: Team member email signing the commit
            owner: Owner of the repo (github.com/[OWNER])
            repo: Name of repo (github.com/[OWNER]/[REPO])
            oauth: Person oauth token with permissions to commit
        """
        self._name = name
        self._email = email
        self._owner = owner
        self._repo = repo
        self.__oauth = oauth
        self.client = http.client.HTTPSConnection("github.com")

    def __str__(self) -> str:
        """ REPL """
        return f"Repo Owner: {self._owner}, Repo Name: {self._repo}"

    def __headers(self) -> dict:
        """ create headers with auth token """
        return {
            "Accept": "application.vnd.github.v3+json",
            "Authorization": f"token {self.__oauth}",
        }

    def _git_post(self, endpoint: str, payload: dict) -> dict:
        """ Private: Handles all posts to git. `operation` is used for influx key """

        self.client.request("POST", endpoint, json.dumps(payload), self.__headers())

        # Decode response
        # TODO error handling
        result = json.loads(self.client.getresponse().read().decode("utf-8"))

        return result

    def get_branch_sha(self, branch_name: str) -> Optional[str]:
        """ Get the SHA of the base branch """
        # https://docs.github.com/en/rest/reference/repos#get-a-branch
        self.client.request(
            "GET",
            f"/api/v3/repos/{self._owner}/{self._repo}/branches/{branch_name}",
            None,
            self.__headers(),
        )

        # Decode response
        # TODO error handling
        result = json.loads(self.client.getresponse().read().decode("utf-8"))

        sha = result.get("commit", {}).get("sha")
        if sha is None:
            self.logger.error("Get SHA failed: %s", result)

        return sha

    def create_branch(self, base_branch: str, new_branch: str) -> Optional[str]:
        """ Creates branch from base branch, return SHA of new branch """
        # https://docs.github.com/en/rest/reference/git#create-a-reference
        endpoint = f"/api/v3/repos/{self._owner}/{self._repo}/git/refs"
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
        endpoint = f"/api/v3/repos/{self._owner}/{self._repo}/git/blobs"
        payload = {
            "owner": self._owner,
            "repo": self._repo,
            "content": file_contents,
            "encoding": "utf-8",
        }

        return self._git_post(endpoint, payload).get("sha", "")

    def create_blob_tree(self, branch_sha: str, file_name: str, blob_sha: str) -> str:
        """ Create a tree link to blob, returns tree sha for commit """
        # https://docs.github.com/en/rest/reference/git#create-a-tree
        endpoint = f"/api/v3/repos/{self._owner}/{self._repo}/git/trees"
        payload = {
            "base_tree": branch_sha,
            "owner": self._owner,
            "repo": self._repo,
            "tree": [
                {
                    "path": file_name,
                    "mode": "100644",
                    "type": "blob",
                    "sha": blob_sha,
                }
            ],
        }
        return self._git_post(endpoint, payload).get("sha", "")

    def create_commit(self, branch_sha: str, tree_sha: str) -> str:
        """ Creates commit to branch """
        # https://docs.github.com/en/rest/reference/git#create-a-blob
        endpoint = f"/api/v3/repos/{self._owner}/{self._repo}/git/commits"
        payload = {
            "message": "Auto commit by AIM Orc WatchTower",
            "author": {
                "name": self._name,
                "email": self._email,
            },
            "parents": [branch_sha],
            "tree": tree_sha,
        }

        return self._git_post(endpoint, payload).get("sha", "")

    def update_reference(self, branch_name: str, commit_sha: str) -> dict:
        """ Create or update the reference of a branch """
        # https://docs.github.com/en/rest/reference/git#update-a-reference
        endpoint = (
            f"/api/v3/repos/{self._owner}/{self._repo}/git/refs/heads/{branch_name}"
        )
        payload = {
            "ref": f"refs/heads/{branch_name}",
            "sha": commit_sha,
        }

        return self._git_post(endpoint, payload)

    def create_pull_request(
        self, base_branch: str, head_branch: str, pr_title: str, pr_body: str
    ) -> dict:
        """ Create PR from head_branch -> base_branch """
        # https://docs.github.com/en/rest/reference/pulls#create-a-pull-request
        endpoint = f"/api/v3/repos/{self._owner}/{self._repo}/pulls"
        payload = {
            "owner": self._owner,
            "repo": self._repo,
            "title": pr_title,
            "head": head_branch,
            "base": base_branch,
            "body": pr_body,
            "maintainer_can_modify": True,
        }

        return self._git_post(endpoint, payload)

    def send_template(
        self,
        base_branch: str,
        new_branch: str,
        file_name: str,
        file_contents: str,
        **kwargs,
    ) -> None:
        """
        Creates a new branch on defined repo, uploads template, makes PR

        Args:
            base_branch: Name of branch that will be the source of new branch
            new_branch: Name of new branch (will fail if exists)
            file_name: Name of file being committed
            file_contents: String of file contents

        Optional Keyword Args:
            pr_title [str]: Title of the pull request
            pr_content [str]: Conent of pull request message
        """
        pr_title = kwargs.get("pr_title", "New automated request")
        pr_body = kwargs.get("pr_content", "Automated PR")

        clean_branch_name = new_branch.replace(" ", "_")
        clean_file_name = file_name.replace(" ", "_")

        new_branch_sha = self.create_branch(base_branch, clean_branch_name)

        if new_branch_sha is None:
            self.logger.critical("Failed to find branch SHA, unable to continue.")
            return

        blob_sha = self.create_blob(file_contents)

        tree_sha = self.create_blob_tree(new_branch_sha, clean_file_name, blob_sha)

        commit_sha = self.create_commit(new_branch_sha, tree_sha)

        self.update_reference(clean_branch_name, commit_sha)

        self.create_pull_request(base_branch, clean_branch_name, pr_title, pr_body)
