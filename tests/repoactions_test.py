"""Unit tests for apiclient.py"""

from __future__ import annotations

import os
from collections.abc import Generator
from unittest.mock import patch

import pytest

from githubclient.repoactions import RepoActions
from githubclient.repoactions import RepoReturn

VALID_MOCK_ENV = {
    "GITHUB_AUTH_TOKEN": "MOCK",
    "GITHUB_USER_NAME": "MOCK",
}


@pytest.fixture(autouse=True)
def mock_environs() -> Generator[None, None, None]:
    with patch.dict(os.environ, VALID_MOCK_ENV):
        yield None


@pytest.fixture
def repo() -> Generator[RepoActions, None, None]:
    yield RepoActions("mock_owner", "mock_repo")


def test_get_branch(repo: RepoActions) -> None:
    resp = {
        "commit": {
            "sha": "mock_sha",
        },
        "url": "mock_url",
        "html_url": "mock_html_url",
    }
    expected_url = "/repos/mock_owner/mock_repo/branches/mock_branch"

    with patch.object(repo.http_client, "git_get", return_value=resp) as mock_get:
        result = repo.get_branch("mock_branch")

    mock_get.assert_called_once_with(expected_url)
    assert result.sha == "mock_sha"
    assert result.url == "mock_url"
    assert result.html_url == "mock_html_url"
    assert result.full_return == resp


def test_create_branch(repo: RepoActions) -> None:
    mock_branch = RepoReturn(sha="mock_sha")
    resp = {
        "object": {
            "sha": "mock_sha",
            "url": "mock_url",
        }
    }
    expected_url = "/repos/mock_owner/mock_repo/git/refs"
    with patch.object(repo.http_client, "git_post", return_value=resp) as mock_post:
        with patch.object(repo, "get_branch", return_value=mock_branch):
            result = repo.create_branch("mock_branch", "mock_new_branch")

    mock_post.assert_called_once_with(
        expected_url,
        {
            "ref": "refs/heads/mock_new_branch",
            "sha": "mock_sha",
        },
    )
    assert result.sha == "mock_sha"
    assert result.url == "mock_url"


def test_create_blob(repo: RepoActions) -> None:
    resp = {"sha": "mock_sha"}
    expected_url = "/repos/mock_owner/mock_repo/git/blobs"
    with patch.object(repo.http_client, "git_post", return_value=resp) as mock_post:
        result = repo.create_blob("mock file contents")

    mock_post.assert_called_once_with(
        expected_url,
        {
            "owner": "mock_owner",
            "repo": "mock_repo",
            "content": "mock file contents",
            "encoding": "utf-8",
        },
    )
    assert result.sha == "mock_sha"


def test_create_blob_tree(repo: RepoActions) -> None:
    resp = {"sha": "mock_sha", "url": "mock_url"}
    expected_url = "/repos/mock_owner/mock_repo/git/trees"
    with patch.object(repo.http_client, "git_post", return_value=resp) as mock_post:
        result = repo.create_blob_tree(
            "mock_branch_sha", [("mock_blob_sha", "file.md")]
        )

    mock_post.assert_called_once_with(
        expected_url,
        {
            "base_tree": "mock_branch_sha",
            "owner": "mock_owner",
            "repo": "mock_repo",
            "tree": [
                {
                    "path": "file.md",
                    "mode": "100644",
                    "type": "blob",
                    "sha": "mock_blob_sha",
                }
            ],
        },
    )
    assert result.sha == "mock_sha"
    assert result.url == "mock_url"


def test_create_commit(repo: RepoActions) -> None:
    resp = {"sha": "mock_sha", "url": "mock_url", "html_url": "mock_html_url"}
    expected_url = "/repos/mock_owner/mock_repo/git/commits"
    with patch.object(repo.http_client, "git_post", return_value=resp) as mock_post:
        result = repo.create_commit(
            "mock_author_name",
            "mock_author_email",
            "mock_branch_sha",
            "mock_tree_sha",
            "mock commit message",
        )

    mock_post.assert_called_once_with(
        expected_url,
        {
            "message": "mock commit message",
            "author": {
                "name": "mock_author_name",
                "email": "mock_author_email",
            },
            "parents": ["mock_branch_sha"],
            "tree": "mock_tree_sha",
        },
    )
    assert result.sha == "mock_sha"
    assert result.url == "mock_url"
    assert result.html_url == "mock_html_url"


def test_update_reference(repo: RepoActions) -> None:
    resp = {"object": {"sha": "mock_sha", "url": "mock_url"}}
    expected_url = "/repos/mock_owner/mock_repo/git/refs/heads/mock_branch"
    with patch.object(repo.http_client, "git_post", return_value=resp) as mock_patch:
        result = repo.update_reference("mock_branch", "mock_sha")

    mock_patch.assert_called_once_with(
        expected_url,
        {
            "ref": "refs/heads/mock_branch",
            "sha": "mock_sha",
        },
    )
    assert result.sha == "mock_sha"


def test_create_pull_request(repo: RepoActions) -> None:
    resp = {"number": 10, "url": "mock_url", "html_url": "mock_html_url"}
    expected_url = "/repos/mock_owner/mock_repo/pulls"
    with patch.object(repo.http_client, "git_post", return_value=resp) as mock_post:
        result = repo.create_pull_request("mock_branch", "mock_base_branch")

    mock_post.assert_called_once_with(
        expected_url,
        {
            "owner": "mock_owner",
            "repo": "mock_repo",
            "title": "Auto PR",
            "head": "mock_branch",
            "base": "mock_base_branch",
            "body": "PR Auto Generated",
            "maintainer_can_modify": True,
            "draft": False,
        },
    )
    assert result.sha == "10"
    assert result.url == "mock_url"
    assert result.html_url == "mock_html_url"


def test_add_lables(repo: RepoActions) -> None:
    resp = [{"name": "MockTest01"}, {"name": "MockTest02"}]
    expected_url = "/repos/mock_owner/mock_repo/issues/10/labels"
    with patch.object(repo.http_client, "git_post", return_value=resp) as mock_post:
        result = repo.add_lables("10", ["MockTest01", "MockTest02"])

    mock_post.assert_called_once_with(
        expected_url,
        {"labels": ["MockTest01", "MockTest02"]},
    )
    assert len(result.full_return) == len(["MockTest01", "MockTest02"])
