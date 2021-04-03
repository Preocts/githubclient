# -*- coding: utf-8 -*-
""" Abstract layer for git API communication

This class gives the methods needed to accomplish the following:
    - Create a new branch in target repo from source branch
    - Upload a template file to the branch
    - Commit the file to the new branch
    - Create a pull request for new branch to source branch
    - Add labels to the pull request

Author: Preocts <preocts@preocts.com>

Usage:
    from gitclient import GitClient

    ...
    # Code to load/create template file as string, utf-8
    ...

    client = GitClient(
        name="YOUR GITHUB NAME",
        email="ASSOCIATED EMAIL",
        owner="REPO-OWNER",  # (github.com/[OWNER]/[REPONAME])
        repo="REPO-NAME",
        oauth="[OAuth Secret Token]",
    )
    client.send_template(
        base_branch="main",
        new_branch="my_cool_branch,
        file_name="cool_template_file.md",
        file_contents="# Hello World",
        pr_title="Pull request Title",
        pr_content="Pull request message",
        labels=["Awesome", ":rooDuck:"]
    )
"""
import re
import json
import logging
import http.client
from string import printable
from typing import List
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
        self.client = http.client.HTTPSConnection("api.github.com")

    def __str__(self) -> str:
        """ REPL """
        return f"Repo Owner: {self._owner}, Repo Name: {self._repo}"

    def __headers(self) -> dict:
        """ create headers with auth token """
        return {
            "Accept": "application.vnd.github.v3+json",
            "User-Agent": self._name,
            "Authorization": f"token {self.__oauth}",
        }

    def _git_post(self, endpoint: str, payload: dict) -> dict:
        """ Private: Handles all posts to git. """

        self.client.request("POST", endpoint, json.dumps(payload), self.__headers())

        # Decode response
        # TODO error handling
        result = json.loads(self.client.getresponse().read().decode("utf-8"))
        return result

    def _git_get(self, endpoint: str) -> dict:
        """ Private: Handles all GET to github. """

        self.client.request("GET", endpoint, None, self.__headers())

        # Decode response
        # TODO error handling
        result = json.loads(self.client.getresponse().read().decode("utf-8"))
        return result

    def get_branch_sha(self, branch_name: str) -> Optional[str]:
        """ Get the SHA of the base branch """
        # https://docs.github.com/en/rest/reference/repos#get-a-branch

        self.logger.debug("Requesting branch SHA")
        endpoint = f"/repos/{self._owner}/{self._repo}/branches/{branch_name}"

        result = self._git_get(endpoint)

        sha = result.get("commit", {}).get("sha")
        if sha is None:
            self.logger.error("Get SHA failed: %s", result)

        return sha

    def create_branch(self, base_branch: str, new_branch: str) -> Optional[str]:
        """ Creates branch from base branch, return SHA of new branch """
        # https://docs.github.com/en/rest/reference/git#create-a-reference

        self.logger.debug("Creating Branch")
        endpoint = f"/repos/{self._owner}/{self._repo}/git/refs"
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
        endpoint = f"/repos/{self._owner}/{self._repo}/git/blobs"
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

        self.logger.debug("Creating Tree")
        endpoint = f"/repos/{self._owner}/{self._repo}/git/trees"
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

        self.logger.debug("Create commit")
        endpoint = f"/repos/{self._owner}/{self._repo}/git/commits"
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

        self.logger.debug("Update branch ref")
        endpoint = f"/repos/{self._owner}/{self._repo}/git/refs/heads/{branch_name}"
        payload = {
            "ref": f"refs/heads/{branch_name}",
            "sha": commit_sha,
        }

        return self._git_post(endpoint, payload)

    def create_pull_request(
        self, base_branch: str, head_branch: str, pr_title: str, pr_body: str
    ) -> Optional[int]:
        """ Create PR from head_branch -> base_branch """
        # https://docs.github.com/en/rest/reference/pulls#create-a-pull-request

        self.logger.debug("Create pull request")
        endpoint = f"/repos/{self._owner}/{self._repo}/pulls"
        payload = {
            "owner": self._owner,
            "repo": self._repo,
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
        params = f"?head={head_branch}"
        endpoint = f"/repos/{self._owner}/{self._repo}/pulls{params}"

        result = self._git_get(endpoint)

        if not isinstance(result, list) or len(result) > 1:
            self.logger.warning("Unable to find exact PR for '%s'", head_branch)
            return None

        return result[0].get("number") if result else None

    def add_lables(self, number: int, labels: List[str]) -> None:
        """ Add labels to a pull request """
        # https://docs.github.com/en/rest/reference/issues#add-labels-to-an-issue

        self.logger.debug("Add labels")
        endpoint = f"repo/{self._owner}/{self._repo}/issues/{number}/labels"
        payload = {
            "labels": labels,
        }

        if labels:
            self._git_post(endpoint, payload)

    def _clean_string(
        self,
        input_: str,
        clean_spaces: bool = False,
        is_branch: bool = False,
        is_file: bool = False,
    ) -> str:
        """
        Strips all non-printable characters from input. Trims leading/trailing space

        Args:
            clean_space: If true will replace spaces with underscores
            is_branch: If true will strip illegal branch characters
            is_file: If true will strip illegal filename characters
        """
        result = ""
        # Regex to find forbidden characters in github branch name
        # https://stackoverflow.com/questions/3651860
        branch_rules = r"/^[\.\/]|\.\.|@{|[\/\.]$|^@$|[~^:\x00-\x20\x7F\s?*[\]\\]"
        # Regex to find forbidden characters in filename
        file_rules = r'[\\/:"*?<>|]+'

        for char in input_:
            if char in printable:
                result += char

        if clean_spaces:
            result = result.replace(" ", "_")

        if is_branch:
            result = re.sub(branch_rules, "", result)

        if is_file:
            result = re.sub(file_rules, "", result)

        if input_ != result:
            self.logger.debug("String altered: '%s' -> '%s'", input_, result)
        return result.strip(" ")

    def send_template(
        self,
        base_branch: str,
        new_branch: str,
        file_name: str,
        file_contents: str,
        **kwargs,
    ) -> bool:
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
            labels [List[str]]: String of labels to apply to pull request
        """
        pr_title = kwargs.get("pr_title", "New automated request")
        pr_body = kwargs.get("pr_content", "Automated PR")
        labels: List[str] = kwargs.get("labels", [])

        clean_branch_name = self._clean_string(new_branch, True, is_branch=True)
        clean_file_name = self._clean_string(file_name, True, is_file=True)

        new_branch_sha = self.create_branch(base_branch, clean_branch_name)

        if not new_branch_sha:
            self.logger.critical("Failed to find branch SHA, unable to continue.")
            return False

        tree_sha = self.create_blob_tree(
            new_branch_sha, clean_file_name, self.create_blob(file_contents)
        )

        commit_sha = self.create_commit(new_branch_sha, tree_sha)

        self.update_reference(clean_branch_name, commit_sha)

        issue_number = self.create_pull_request(
            base_branch, clean_branch_name, pr_title, pr_body
        )

        if not issue_number:
            self.logger.critical("No issue number returned, unable to complete.")
            return False

        self.add_lables(issue_number, labels)
        return True
