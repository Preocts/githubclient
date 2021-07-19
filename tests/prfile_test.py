"""Unit testing for prfile.py"""
import datetime
import os
from unittest.mock import patch

import pytest
from githubclient import prfile


NOW = datetime.datetime.now().strftime("%h%s")
TEST_TOML = "tests/fixtures/.repoconfig_test.toml"
MOCK_FILES = ["filename01.txt", "filename02.txt"]


def test_parser_no_args() -> None:
    """Raise SystemExit with no args test"""
    with pytest.raises(SystemExit):
        _ = prfile.cli_parser([])


def test_parser_file_names() -> None:
    """Get list of filenames"""

    args = prfile.cli_parser(MOCK_FILES)

    for filename in MOCK_FILES:
        assert filename in args.filenames


def test_file_exists() -> None:
    """Check for files in current working directory"""
    assert prfile.file_exists("setup.cfg")
    assert not prfile.file_exists("setup.not.there")


def test_create_empty_config() -> None:
    """Create a config file that doesn't exist"""
    assert not prfile.file_exists(NOW)

    prfile.create_empty_config(NOW)

    assert prfile.file_exists(NOW)

    os.remove(NOW)


def test_load_toml() -> None:
    """Load test fixture toml"""
    result = prfile.load_config(TEST_TOML)

    assert result.ownername
    assert result.reponame
    assert result.useremail
    assert result.username
    assert result.usertoken


def test_main() -> None:
    """Should load dry (no config) and with empty config"""
    filename = f"tests/fixtures/temp_{NOW}"

    assert not os.path.isfile(filename)

    with patch.object(prfile, "CONFIG_FILE", filename):
        prfile.main(prfile.cli_parser(MOCK_FILES))

        assert os.path.isfile(filename)

        prfile.main(prfile.cli_parser(MOCK_FILES))

        os.remove(filename)
