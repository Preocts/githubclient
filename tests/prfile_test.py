"""Unit testing for prfile.py"""
import pytest
from githubclient.prfile import cli_parser
from githubclient.prfile import file_exists


def test_parser_no_args() -> None:
    """Raise SystemExit with no args test"""
    with pytest.raises(SystemExit):
        _ = cli_parser([])


def test_parser_file_names() -> None:
    """Get list of filenames"""
    user_input = ["filename01.txt", "filename02.txt"]

    args = cli_parser(user_input)

    for filename in user_input:
        assert filename in args.filenames


def test_file_exists() -> None:
    """Check for files in current working directory"""
    assert file_exists("setup.cfg")
    assert not file_exists("setup.not.there")
