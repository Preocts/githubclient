"""Unit tests for apiclient.py"""
import os
from unittest.mock import patch

import pytest
from githubclient.apiclient import APIClient

VALID_MOCK_ENV = {
    "GITHUB_AUTH_TOKEN": "MOCK",
    "GITHUB_USER_NAME": "MOCK",
}


def test_env_loaded() -> None:
    """A token exists"""
    with patch.dict(os.environ, VALID_MOCK_ENV):
        _ = APIClient()


def test_missing_env_token() -> None:
    """Stop if token is missing"""
    with patch.dict(os.environ, {"GITHUB_AUTH_TOKEN": "", "GITHUB_USER_NAME": "MOCK"}):
        with pytest.raises(ValueError):
            _ = APIClient()


def test_missing_env_username() -> None:
    """Stop if token is missing"""
    with patch.dict(os.environ, {"GITHUB_AUTH_TOKEN": "MOCK", "GITHUB_USER_NAME": ""}):
        with pytest.raises(ValueError):
            _ = APIClient()


def test_jsonify() -> None:
    """Convert bytes to json or return bytes in error"""
    valid = '{"test": "response"}'.encode()
    invalid = "test: response".encode()

    assert isinstance(APIClient._jsonify(valid), dict)
    assert APIClient._jsonify(invalid) == {"error": invalid}
