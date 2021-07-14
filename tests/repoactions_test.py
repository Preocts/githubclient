"""Unit tests for apiclient.py"""
import os
from typing import Generator
from unittest.mock import patch

import pytest
import vcr
from secretbox.loadenv import LoadEnv
# from githubclient.apiclient import APIClient

_ = LoadEnv(auto_load=True)

TEST_USER = "Preocts"
MOCK_ENV = {
    "GITHUB_AUTH_TOKEN": "MOCK",
    "GITHUB_USER_NAME": "MOCK",
}

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
