"""Unit tests for apiclient.py"""
from __future__ import annotations

import os
from collections.abc import Generator
from unittest.mock import patch

import pytest
import vcr
from githubclient.repoactions import RepoActions
from secretbox import SecretBox

TEST_REPO = "gitclient_test"
TEST_OWNER = "Preocts"
TEST_BRANCH = "main"
TEST_NEW_BRANCH = "main2"

MOCK_ENV = {
    "GITHUB_AUTH_TOKEN": "MOCK",
    "GITHUB_USER_NAME": "MOCK",
}

# VCR FILE NAMES
GET_BRANCH_GOOD = "get_branch_success.yaml"
GET_BRANCH_FAIL = "get_branch_fail.yaml"
CREATE_BRANCH_GOOD = "create_branch_success.yaml"
CREATE_BRANCH_FAIL = "create_branch_fail.yaml"
CREATE_BLOBS_GOOD = "create_blobs_success.yaml"
CREATE_TREE_GOOD = "create_tree_success.yaml"
CREATE_COMMIT_GOOD = "create_commit_success.yaml"
UPDATE_REF_GOOD = "update_ref_success.yaml"
CREATE_PR_GOOD = "create_pr_success.yaml"
ADD_LABELS_GOOD = "add_labels_success.yaml"

# TEST REQUIRED SHA VALUES
# NOTE: Would love to have a better way here.
# These are pulled from each test, used in the next
NEW_BRANCH_SHA = "08746b8758f3f2047ab3720a5b1b457dfb7f11bf"
NEW_BLOBS_SHA = [
    ("e5b064423801f1397792727eb6d25dfb0552cea7", "file01.txt"),
    ("0257d4d2d3d5f1acf80e7d1832274b76865bbab9", "file02.txt"),
]
NEW_TREE_SHA = "b52e7bad122209b1c11d27c5eaf84e99e513ef65"
NEW_COMMIT_SHA = "4e51a63f07f40f59823d35b0b9fe019ddfd6357b"
NEW_PR_NUMBER = "8"


gitvcr = vcr.VCR(
    record_mode="once",
    filter_headers=["Authorization"],
    match_on=["uri", "method"],
    serializer="yaml",
    cassette_library_dir="tests/fixtures",
)


@pytest.fixture(scope="function", name="envmock")
def fixture_envmock() -> Generator[None, None, None]:
    """Inject mock environ vars"""
    with patch.dict(os.environ, MOCK_ENV):
        yield None


@pytest.fixture(scope="function", name="repo")
def fixture_repo(envmock: None) -> Generator[RepoActions, None, None]:
    """Create the client fixture"""
    _ = SecretBox(auto_load=True)

    yield RepoActions(TEST_OWNER, TEST_REPO)


def test_get_branch_success(repo: RepoActions) -> None:
    """Successful pull branch"""

    with gitvcr.use_cassette(GET_BRANCH_GOOD):
        result = repo.get_branch(TEST_BRANCH)

    assert result.sha


def test_get_branch_fail(repo: RepoActions) -> None:
    """Fail to pull branch"""
    # NOTE: Assumes TEST_BRANCH*3 does not exist
    with gitvcr.use_cassette(GET_BRANCH_FAIL):
        result = repo.get_branch(TEST_BRANCH * 3)

    assert not result.sha


def test_create_branch_success(repo: RepoActions) -> None:
    """Succeful create branch"""

    with gitvcr.use_cassette(CREATE_BRANCH_GOOD):
        result = repo.create_branch(TEST_BRANCH, TEST_NEW_BRANCH)

    assert result.sha


def test_create_branch_fail(repo: RepoActions) -> None:
    """Fail to create a branch because existing and invalid"""

    with gitvcr.use_cassette(CREATE_BRANCH_FAIL):
        result = repo.create_branch(TEST_BRANCH, TEST_BRANCH)

        assert not result.sha

        result = repo.create_branch(TEST_BRANCH, f"{TEST_BRANCH}*{TEST_BRANCH}")

        assert not result.sha


def test_create_blob(repo: RepoActions) -> None:
    """Create two blobs"""
    mock_blob01 = "There once was a tree on a hill"
    mock_blob02 = "The end"

    with gitvcr.use_cassette(CREATE_BLOBS_GOOD):
        blob01 = repo.create_blob(mock_blob01)
        blob02 = repo.create_blob(mock_blob02)

    assert blob01.sha
    assert blob02.sha


def test_create_tree_success(repo: RepoActions) -> None:
    """Create a tree"""

    with gitvcr.use_cassette(CREATE_TREE_GOOD):
        result = repo.create_blob_tree(NEW_BRANCH_SHA, NEW_BLOBS_SHA)

    assert result.sha


def test_commit_success(repo: RepoActions) -> None:
    """Create a commit"""
    commit_msg = "Hot new commit"

    with gitvcr.use_cassette(CREATE_COMMIT_GOOD):
        result = repo.create_commit(
            author_name=TEST_OWNER,
            author_email=f"{TEST_OWNER}@example.com",
            branch_sha=NEW_BRANCH_SHA,
            tree_sha=NEW_TREE_SHA,
            message=commit_msg,
        )

    assert result.sha
    assert result.full_return.get("message", "") == commit_msg


def test_update_reference_success(repo: RepoActions) -> None:
    """Update a branch's reference"""

    with gitvcr.use_cassette(UPDATE_REF_GOOD):
        result = repo.update_reference(TEST_NEW_BRANCH, NEW_COMMIT_SHA)

    assert result.sha


def test_create_pr_success(repo: RepoActions) -> None:
    """Create pull request"""

    with gitvcr.use_cassette(CREATE_PR_GOOD):
        result = repo.create_pull_request(TEST_NEW_BRANCH, TEST_BRANCH)

    assert result.sha
    assert isinstance(result.sha, str)


def test_add_labels_success(repo: RepoActions) -> None:
    """Add some labels"""
    labels = ["MockTest01", "MockTest02"]
    with gitvcr.use_cassette(ADD_LABELS_GOOD):
        result = repo.add_lables(NEW_PR_NUMBER, labels)

    assert len(result.full_return) == len(labels)
