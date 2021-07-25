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


def test_main_cli() -> None:
    """Check CLI input"""
    with patch.object(prfile, "cli_parser") as cli_parser:
        with patch.object(prfile, "main", return_value=1) as main:

            with pytest.raises(SystemExit):
                prfile.main_cli()

            main.assert_called_once()
            cli_parser.assert_called_once()


def test_main() -> None:
    """Should load dry (no config) and with empty config"""
    filename = f"tests/fixtures/temp_{NOW}"

    assert not os.path.isfile(filename)

    with patch.object(prfile, "CONFIG_FILE", filename):
        with patch("builtins.input", lambda user_in: "mock"):
            with patch.object(prfile, "run_user_prompt"):
                with patch.object(prfile, "RepoActions"):
                    with pytest.raises(FileNotFoundError):
                        prfile.main(prfile.cli_parser(MOCK_FILES))

                    result = prfile.main(prfile.cli_parser(VALID_FILES))

        assert os.path.isfile(filename)

    os.remove(filename)

    assert result == 0


def test_main_error() -> None:
    """Mock failure at GitHub process"""
    filename = f"tests/fixtures/temp_{NOW}"

    assert not os.path.isfile(filename)

    with patch.object(prfile, "CONFIG_FILE", filename):
        with patch("builtins.input", lambda user_in: "mock"):
            with patch.object(prfile, "run_user_prompt"):
                with patch.object(prfile, "create_pull_request", return_value=""):

                    result = prfile.main(prfile.cli_parser(VALID_FILES))

        assert os.path.isfile(filename)

    os.remove(filename)

    assert result == 1


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
    assert result.basebranch

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


def test_user_prompt() -> None:
    with patch("builtins.input", lambda user_in: "hello"):
        result = prfile.get_input("")
        assert result == "hello"


def test_run_user_prompt() -> None:
    """Runs the gambit of possible user prompts"""
    user_inputs = ["T", "mock", "m", "mock", "s"]

    with patch.object(prfile, "get_input", side_effect=user_inputs):
        result = prfile.run_user_prompt()

    assert result.message == "mock"
    assert result.title == "mock"


def test_run_user_prompt_defaults() -> None:
    """Blanks title and message, assert restore of defaults"""
    user_inputs = ["t", "", "m", "", "s"]

    with patch.object(prfile, "get_input", side_effect=user_inputs):
        result = prfile.run_user_prompt()

    assert result.message == prfile.DEFAULT_MESSAGE
    assert result.title == prfile.DEFAULT_TITLE


def test_run_user_prompt_abort() -> None:
    """Let us escape"""
    user_inputs = ["", "", "", "", "a"]

    with patch.object(prfile, "get_input", side_effect=user_inputs) as mocked:
        with pytest.raises(SystemExit):
            _ = prfile.run_user_prompt()

        assert mocked.call_count == 5
