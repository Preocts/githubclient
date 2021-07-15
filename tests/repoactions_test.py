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

GET_BRANCH_GOOD = "get_branch_success.yaml"
GET_BRANCH_FAIL = "get_branch_fail.yaml"
CREATE_BRANCH_GOOD = "create_branch_success.yaml"
CREATE_BRANCH_FAIL = "create_branch_fail.yaml"

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

    assert result


def test_get_branch_fail(repo: RepoActions) -> None:
    """Fail to pull branch"""
    # NOTE: Assumes TEST_BRANCH*3 does not exist
    with gitvcr.use_cassette(GET_BRANCH_FAIL):
        result = repo.get_branch(TEST_BRANCH * 3)

    assert not result


def test_create_branch_success(repo: RepoActions) -> None:
    """Succeful create branch"""

    with gitvcr.use_cassette(CREATE_BRANCH_GOOD):
        result = repo.create_branch(TEST_BRANCH, TEST_NEW_BRANCH)

    assert result


def test_create_branch_fail(repo: RepoActions) -> None:
    """Fail to create a branch because existing and invalid"""

    with gitvcr.use_cassette(CREATE_BRANCH_FAIL):
        result = repo.create_branch(TEST_BRANCH, TEST_BRANCH)

        assert not result

        result = repo.create_branch(TEST_BRANCH, f"{TEST_BRANCH}*{TEST_BRANCH}")

        assert not result
