"""
CLI Controls for creates a PR with a file

All commands can be given 'global'

Commands:
    --repo-name
    --owner-name
    --name
    --email
    --auth-token
    --
Author: Preocts <Preocts#8196>
"""
import argparse
import pathlib
import sys
from typing import Optional
from typing import Sequence

REPO_URL = "https://github.com/Preocts/githubclient"
CONFIG_FILE = ".default_config.toml"
CWD = pathlib.Path.cwd()


def cli_parser(args: Optional[Sequence[str]] = None) -> argparse.Namespace:
    """Configure argparse"""
    parser = argparse.ArgumentParser(
        prog="prfiles",
        description="Add files to a repo on a unique branch and create a Pull Request.",
        epilog=f"Check it. {REPO_URL}",
    )
    parser.add_argument(
        "filenames",
        nargs="+",
        help="One, or more, files to be added to the pull request (utf-8 encoding)",
    )

    parser.add_argument(
        "--repo-name",
        help="Set name of target repo (https://github.com/[owner name]/[repo name])",
    )
    parser.add_argument(
        "--owner-name",
        help="Set repo's owner name (https://github.com/[owner name]/[repo name])",
    )
    parser.add_argument("--email", help="Set your GitHub email for pull requests")
    parser.add_argument("--name", help="Set your GitHub user name")
    parser.add_argument(
        "--auth-token",
        help="Set the developer auth-token (must have 'public_repo' access)",
    )
    return parser.parse_args() if args is None else parser.parse_args(args)


def main(args: argparse.Namespace) -> int:
    """Main CLI process"""
    print("Meow")
    print(args)
    print(pathlib.Path.cwd())
    return 0


def file_exists(filename: str) -> bool:
    """Checks for the existance of file in current working directory"""
    return pathlib.Path.exists(CWD / filename)


if __name__ == "__main__":
    sys.exit(main(cli_parser()))
