"""Unit testing for prfile.py"""
import datetime
import os
import pathlib
from unittest.mock import patch

import pytest
from githubclient import prfile


NOW = datetime.datetime.now().strftime("%H%M%S")
TEST_TOML = "tests/fixtures/.repoconfig_test.toml"
MOCK_FILES = ["filename01.txt", "filename02.txt"]
VALID_FILES = ["./tests/prfile_test.py", "./tests/repoactions_test.py"]


def test_main() -> None:
    """Should load dry (no config) and with empty config"""
    filename = f"tests/fixtures/temp_{NOW}"

    assert not os.path.isfile(filename)

    with patch.object(prfile, "CONFIG_FILE", filename):
        with patch("builtins.input", lambda user_in: "mock"):
            with pytest.raises(FileNotFoundError):
                prfile.main(prfile.cli_parser(MOCK_FILES))

            prfile.main(prfile.cli_parser(VALID_FILES))

        assert os.path.isfile(filename)

        os.remove(filename)


def test_parser_file_names() -> None:
    """Get list of filenames"""

    args = prfile.cli_parser(MOCK_FILES)

    for filename in MOCK_FILES:
        assert filename in args.filenames


def test_create_empty_config() -> None:
    """Create a config file that doesn't exist"""
    assert not pathlib.Path(NOW).exists()

    prfile.save_config(NOW, prfile.RepoConfig())

    assert pathlib.Path(NOW).exists()

    os.remove(NOW)


def test_load_toml() -> None:
    """Load test fixture toml"""
    empty_args = prfile.cli_parser([])
    user_args = prfile.cli_parser(["--username", "Preocts"])

    result = prfile.load_config(TEST_TOML, empty_args)

    assert result.ownername
    assert result.reponame
    assert result.useremail
    assert result.username
    assert result.usertoken

    result = prfile.load_config(TEST_TOML, user_args)

    assert result.username == "Preocts"


def test_fill_config() -> None:
    """Prompt for user data we are missing"""
    config = prfile.RepoConfig(reponame="Testing")

    with patch("builtins.input", lambda user_in: "mock"):

        result = prfile.fill_config(config)

        for key, value in result._asdict().items():
            if key == "reponame":
                assert value == "Testing"
            else:
                assert value == "mock"


def test_all_files_exist() -> None:
    """File existance"""

    assert prfile.all_files_exist(VALID_FILES)

    assert not prfile.all_files_exist(MOCK_FILES)
    assert not prfile.all_files_exist([])
