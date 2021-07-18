"""Unit testing for prfile.py"""
import pytest
from prfile import cli_parser


def test_parser_no_args() -> None:
    """Raise SystemExit with no args test"""
    with pytest.raises(SystemExit):
        _ = cli_parser()


def test_parser_file_names() -> None:
    """Get list of filenames"""
    user_input = ["filename01.txt", "filename02.txt"]

    args = cli_parser(user_input)

    for filename in user_input:
        assert filename in args.filenames
