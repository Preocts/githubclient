"""Unit tests for apiclient.py"""
import os
from typing import Generator
from unittest.mock import patch

import pytest
import vcr
from githubclient.repoactions import RepoActions
from secretbox.loadenv import LoadEnv

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

# TEST REQUIRED SHA VALUES
# NOTE: Would love to have a better way here.
# These are pulled from each test, used in the next
NEW_BRANCH_SHA = "08746b8758f3f2047ab3720a5b1b457dfb7f11bf"
NEW_BLOBS_SHA = [
    ("e5b064423801f1397792727eb6d25dfb0552cea7", "file01.txt"),
    ("0257d4d2d3d5f1acf80e7d1832274b76865bbab9", "file02.txt"),
]
NEW_TREE_SHA = ""
NEW_COMMIT_SHA = ""


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
    _ = LoadEnv(auto_load=True)

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


def test_create_tree(repo: RepoActions) -> None:
    """Create a tree"""

    with gitvcr.use_cassette(CREATE_TREE_GOOD):
        result = repo.create_blob_tree(NEW_BRANCH_SHA, NEW_BLOBS_SHA)

    assert result.sha
