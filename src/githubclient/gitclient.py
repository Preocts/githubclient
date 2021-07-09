# -*- coding: utf-8 -*-
""" Create branch, add file, and make pull request using GitHub API

Since: 2021.04.09
Author: Preocts <preocts@preocts.com>
GitHub: https://github.com/Preocts/githubclient
"""
import logging
import re
from string import printable
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Tuple

from githubclient.gitapi import GitAPI


class FileObj(NamedTuple):
    """ Defines values for creating a blob, path is optional """

    file_contents: str
    file_name: str
    file_path: str = ""


class GitClient:
    """ Methods for creating branch, adding files, committing, and pull requests """

    logger = logging.getLogger(__name__)

    def __init__(self, owner: str, repo: str, oauth: str) -> None:
        """
        Initialize to specific repo with personal auth token

        Args:
            owner: Owner of repo, 'github.com/[OWNER]/[REPONAME]'
            repo: Name of repo, 'github.com/[OWNER]/[REPONAME]'
            oauth: Perosonal Auth token with minimum "public_repo" permissions
        """
        self.api = GitAPI(owner, repo, oauth)
        self.branch_name: Optional[str] = None
        self.branch_sha: Optional[str] = None
        self.tree_sha: Optional[str] = None
        self.issue_number: Optional[int] = None

    def create_branch(self, base_branch: str, new_branch: str) -> bool:
        """ Creates a new branch from the base branch """
        self.logger.debug("Create Branch: %s, %s", base_branch, new_branch)

        self.branch_name = new_branch

        self.branch_sha = self.api.create_branch(base_branch, new_branch)

        return bool(self.branch_sha)

    def add_files(self, file_objs: List[FileObj]) -> bool:
        """ Creates a file and adds it to the stage """
        self.logger.debug("Add files, total to process: %d", len(file_objs))
        if not self.branch_sha:
            raise Exception("No branch SHA found. Run create_branch() first.")

        blobs: List[Tuple[str, str]] = []

        for obj in file_objs:
            blob_sha = self.api.create_blob(obj.file_contents)
            if not blob_sha:
                self.logger.error("Failed to create blob for %s", obj.file_name)
            else:
                blobs.append((blob_sha, GitClient.__path(obj)))

        self.tree_sha = self.api.create_blob_tree(self.branch_sha, blobs)

        return bool(self.tree_sha)

    def create_commit(self, author_name: str, author_email: str) -> bool:
        """ Commits any changes to created branch, updates branch reference """
        self.logger.debug("Commit: %s -> %s", self.branch_sha, self.tree_sha)
        if not self.branch_sha or not self.branch_name:
            raise Exception("Missing branch info. Run create_branch() first.")
        if not self.tree_sha:
            raise Exception("No tree SHA found. Run add_files() first.")

        commit_sha = self.api.create_commit(
            author_name, author_email, self.branch_sha, self.tree_sha
        )

        if not commit_sha:
            return False

        ref_sha = self.api.update_reference(self.branch_name, commit_sha)

        return bool(ref_sha)

    def create_pull(self, base_branch: str, title: str, message: str) -> bool:
        """ Create a pull request of new_branch into base_branch """
        self.logger.debug("Create Pull %s <- %s", base_branch, self.branch_name)
        if not self.branch_name:
            raise Exception("Missing branch name. Run create_branch() first.")

        self.issue_number = self.api.create_pull_request(
            base_branch, self.branch_name, title, message
        )

        return bool(self.issue_number)

    def apply_labels(self, labels: List[str]) -> None:
        """ Applies list of labels to pull request, will create if needed """
        if not self.issue_number:
            raise Exception("No issue number availabe. Run create_pull() first.")

        self.api.add_lables(self.issue_number, labels)

    @staticmethod
    def __path(obj: FileObj) -> str:
        """ Assembles path, ensures leading and trailing are clean """
        if obj.file_path and not obj.file_path.endswith("/"):
            path = obj.file_path + "/"
        else:
            path = obj.file_path

        file_path = f"{path}{obj.file_name}".rstrip("/")
        return file_path.strip()

    @staticmethod
    def clean_string(
        content: str,
        clean_spaces: bool = False,
        is_branch: bool = False,
        is_file: bool = False,
    ) -> str:
        """
        Strips all non-printable characters from input. Trims leading/trailing space

        Args:
            content: String to clean
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

        for char in content:
            if char in printable:
                result += char

        if clean_spaces:
            result = result.replace(" ", "_")

        if is_branch:
            result = re.sub(branch_rules, "", result)

        if is_file:
            result = re.sub(file_rules, "", result)

        return result.strip(" ")
