"""Unit tests for apiclient.py"""
import os
from unittest.mock import patch

import pytest
from githubclient.apiclient import APIClient


def test_env_loaded() -> None:
    """A token exists"""
    with patch.dict(os.environ, {"GITHUB_AUTH_TOKEN": "MOCK"}):
        _ = APIClient()


def test_missing_env() -> None:
    """Stop if token is missing"""
    with patch.dict(os.environ, {"GITHUB_AUTH_TOKEN": ""}):
        with pytest.raises(ValueError):
            _ = APIClient()
