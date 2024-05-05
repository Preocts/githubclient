"""Unit tests for apiclient.py"""

from __future__ import annotations

import json
import os
from collections.abc import Generator
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from githubclient.httpclient import HTTPClient

TEST_USER = "Preocts"
VALID_MOCK_ENV = {
    "GITHUB_AUTH_TOKEN": "MOCK",
    "GITHUB_USER_NAME": "MOCK",
}


class MockValidResp:
    def __init__(self):
        self.status = 200
        self.reason = "OK"
        self.read = MagicMock(return_value=b'{"test": "response"}')


class MockInvalidResp:
    def __init__(self):
        self.status = 400
        self.reason = "Bad Request"
        self.read = MagicMock(return_value=b"test: response")


@pytest.fixture(autouse=True)
def mock_environs() -> Generator[None, None, None]:
    with patch.dict(os.environ, VALID_MOCK_ENV):
        yield None


@pytest.fixture
def client() -> Generator[HTTPClient, None, None]:
    client_ = HTTPClient()
    with patch.object(client_.apiclient, "request"):
        yield client_


def test_missing_env_token() -> None:
    with patch.dict(os.environ, {"GITHUB_AUTH_TOKEN": ""}):
        with pytest.raises(EnvironmentError):
            HTTPClient()


def test_missing_env_username() -> None:
    with patch.dict(os.environ, {"GITHUB_USER_NAME": ""}):
        with pytest.raises(EnvironmentError):
            HTTPClient()


def test_jsonify() -> None:
    valid = b'{"test": "response"}'
    invalid = b"test: response"

    assert isinstance(HTTPClient._jsonify(valid), dict)
    assert HTTPClient._jsonify(invalid) == {"error": invalid}


def test_get(client: HTTPClient) -> None:
    with patch.object(client.apiclient, "getresponse", return_value=MockValidResp()):
        result = client.git_get("/users/Preocts")

    assert result["test"] == "response"
    client.apiclient.request.assert_called_once_with(  # type: ignore # fixture mock
        method="GET",
        url="/users/Preocts",
        headers=client.headers,
    )


def test_post(client: HTTPClient) -> None:
    payload = {
        "description": "Unit test",
        "files": {
            "unittest.md": {
                "content": "# Egg",
            },
        },
        "public": True,
    }

    with patch.object(client.apiclient, "getresponse", return_value=MockValidResp()):
        result = client.git_post("/gists", payload)

    assert result["test"] == "response"
    client.apiclient.request.assert_called_once_with(  # type: ignore # fixture mock
        method="POST",
        url="/gists",
        headers=client.headers,
        body=json.dumps(payload),
    )


def test_get_failure(client: HTTPClient) -> None:
    with patch.object(client.apiclient, "getresponse", return_value=MockInvalidResp()):
        result = client.git_get("/users/Preocts")

    assert result["error"] == b"test: response"


def test_post_failure(client: HTTPClient) -> None:
    payload = {
        "description": "Unit test",
        "files": {
            "unittest.md": {
                "content": "# Egg",
            },
        },
        "public": True,
    }

    with patch.object(client.apiclient, "getresponse", return_value=MockInvalidResp()):
        result = client.git_post("/gists", payload)

    assert result["error"] == b"test: response"
