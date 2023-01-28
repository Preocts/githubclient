"""Unit tests for apiclient.py"""
from __future__ import annotations

import os
from typing import Any
from unittest.mock import patch

import vcr
from githubclient.apiclient import APIClient

TEST_USER = "Preocts"
VALID_MOCK_ENV = {
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


def test_env_loaded() -> None:
    """A token exists"""
    with patch.dict(os.environ, VALID_MOCK_ENV):
        _ = APIClient()


def test_missing_env_token(caplog: Any) -> None:
    """Stop if token is missing"""
    with patch.dict(os.environ, {"GITHUB_AUTH_TOKEN": "", "GITHUB_USER_NAME": "MOCK"}):
        _ = APIClient()

        assert "Missing GITHUB_AUTH_TOKEN" in caplog.text


def test_missing_env_username(caplog: Any) -> None:
    """Stop if token is missing"""
    with patch.dict(os.environ, {"GITHUB_AUTH_TOKEN": "MOCK", "GITHUB_USER_NAME": ""}):
        _ = APIClient()

        assert "Missing GITHUB_USER_NAME" in caplog.text


def test_jsonify() -> None:
    """Convert bytes to json or return bytes in error"""
    valid = b'{"test": "response"}'
    invalid = b"test: response"

    assert isinstance(APIClient._jsonify(valid), dict)
    assert APIClient._jsonify(invalid) == {"error": invalid}


def test_get() -> None:
    """Recorded GET test"""
    client = APIClient()

    with gitvcr.use_cassette("test_get.yaml"):
        result = client.git_get("/users/" + TEST_USER)

    assert "error" not in result


def test_post() -> None:
    """Recorded POST test"""
    client = APIClient()
    payload = {
        "description": "Unit test",
        "files": {
            "unittest.md": {
                "content": "# Egg",
            },
        },
        "public": True,
    }

    with gitvcr.use_cassette("test_post.yaml"):
        result = client.git_post("/gists", payload)

    assert result["description"] == payload["description"]
