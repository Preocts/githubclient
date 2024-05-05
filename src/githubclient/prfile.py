"""
CLI Controls for creates a PR with a file

Author: Preocts <Preocts#8196>
"""

from __future__ import annotations

import argparse
import logging
import os
import pathlib
import sys
from collections.abc import Sequence
from configparser import ConfigParser
from datetime import datetime
from typing import NamedTuple

from githubclient.repoactions import RepoActions

REPO_URL = "https://github.com/Preocts/githubclient"
CONFIG_FILE = ".default_config.ini"
CONFIG_SECTION = "GITHUBCLIENT"
CWD = pathlib.Path.cwd()
DEFAULT_NEW_BRANCH = datetime.now().strftime("%Y%m%d.%H%M%S")
DEFAULT_TITLE = f"{DEFAULT_NEW_BRANCH} - Automated PR request"
DEFAULT_MESSAGE = f"{DEFAULT_NEW_BRANCH} - Automated PR request"


class PromptValues(NamedTuple):
    """Dataclass to hold prompt values"""

    new_branch: str
    title: str
    message: str


class RepoConfig(NamedTuple):
    """Dataclass to hold config for repo actions"""

    reponame: str = ""
    ownername: str = ""
    username: str = ""
    useremail: str = ""
    usertoken: str = ""
    basebranch: str = ""

    def to_configparser(self) -> ConfigParser:
        """Return as ConfigParser."""
        config = ConfigParser()
        config[CONFIG_SECTION] = {
            "reponame": self.reponame,
            "ownername": self.ownername,
            "username": self.username,
            "useremail": self.useremail,
            "usertoken": self.usertoken,
            "basebranch": self.basebranch,
        }
        return config

    @classmethod
    def from_configparser(cls, configparser: ConfigParser) -> RepoConfig:
        """Generate class from ConfigParser."""
        if CONFIG_SECTION not in configparser:
            return cls()
        section = configparser[CONFIG_SECTION]
        return cls(
            reponame=section.get("reponame", ""),
            ownername=section.get("ownername", ""),
            username=section.get("username", ""),
            useremail=section.get("useremail", ""),
            usertoken=section.get("usertoken", ""),
            basebranch=section.get("basebranch", ""),
        )


def cli_parser(args: Sequence[str] | None = None) -> argparse.Namespace:
    """Configure argparse"""
    parser = argparse.ArgumentParser(
        prog="prfiles",
        description="Add files to a repo on a unique branch and create a Pull Request.",
        epilog=f"Check it. {REPO_URL}",
    )
    parser.add_argument(
        "filenames",
        type=str,
        nargs="*",
        help="One, or more, files to be added to the pull request (utf-8 encoding)",
    )
    parser.add_argument(
        "--reponame",
        type=str,
        help="Set name of target repo (https://github.com/[owner name]/[repo name])",
    )
    parser.add_argument(
        "--ownername",
        type=str,
        help="Set repo's owner name (https://github.com/[owner name]/[repo name])",
    )
    parser.add_argument(
        "--username",
        type=str,
        help="Set your GitHub user name",
    )
    parser.add_argument(
        "--useremail",
        type=str,
        help="Set your GitHub email for pull requests",
    )
    parser.add_argument(
        "--basebranch",
        type=str,
        help="Set the base branch from which pull requests will be created",
    )
    parser.add_argument(
        "--usertoken",
        type=str,
        help="Set the developer auth-token (must have 'public_repo' access)",
    )
    parser.add_argument(
        "--draft",
        dest="draft",
        action="store_true",
        help="Submit pull request as a draft.",
    )
    parser.add_argument(
        "--debug",
        dest="debug",
        action="store_true",
        help="Turns internal logging level to DEBUG.",
    )
    return parser.parse_args() if args is None else parser.parse_args(args)


def main_cli() -> None:
    """CLI Point of Entry"""
    sys.exit(main(cli_parser()))


def main(args: argparse.Namespace) -> int:
    """Main CLI process"""
    logging.basicConfig(level="DEBUG" if args.debug else "ERROR")

    config = fill_config(load_config(CONFIG_FILE, args))
    save_config(CONFIG_FILE, config)

    if not all_files_exist(args.filenames):
        raise FileNotFoundError(f"Unable to find files: {args.filenames}")

    prompt_values = run_user_prompt()

    inject_env_secrets(config)

    result = create_pull_request(prompt_values, config, args.filenames, args.draft)

    if result:
        opt_word = " draft " if args.draft else " "
        print(f"Pull request{opt_word}created: ", end="")
        print(result)
    else:
        print("Something went wrong...")

    return 0 if result else 1


def get_input(prompt: str) -> str:
    """Get user input"""
    return input(prompt)


def run_user_prompt() -> PromptValues:
    """Allow user to update values or abort"""
    new_branch = DEFAULT_NEW_BRANCH
    title = DEFAULT_TITLE
    message = DEFAULT_MESSAGE
    input_prompt = "set (t)itle, set (m)essage, (s)ubmit, (a)bort (t/m/s/a)? "
    uinput = ""

    while uinput != "s":
        print(f"\nNew Branch: {new_branch}")
        print(f"PR Title  : {title}")
        print(f"PR Message: {message}")
        print("-" * 20)
        uinput = get_input(input_prompt).lower()
        if uinput == "a":
            sys.exit(1)
        elif uinput == "t":
            title = get_input("Enter new title: ")
        elif uinput == "m":
            message = get_input("Enter new message: ")

    return PromptValues(
        new_branch=new_branch if new_branch else DEFAULT_NEW_BRANCH,
        title=title if title else DEFAULT_TITLE,
        message=message if message else DEFAULT_MESSAGE,
    )


def save_config(filename: str, config: RepoConfig) -> None:
    """Save RepoConfig as ini in current working directory."""
    RepoConfig.to_configparser(config).write(open(filename, "w"))


def load_config(filename: str, args: argparse.Namespace) -> RepoConfig:
    """Load config ini, merge with and CLI optionals."""
    parser = ConfigParser()
    parser.read(filename)
    config = RepoConfig.from_configparser(parser)
    return RepoConfig(
        reponame=config.reponame if args.reponame is None else args.reponame,
        ownername=config.ownername if args.ownername is None else args.ownername,
        username=config.username if args.username is None else args.username,
        useremail=config.useremail if args.useremail is None else args.useremail,
        usertoken=config.usertoken if args.usertoken is None else args.usertoken,
        basebranch=config.basebranch if args.basebranch is None else args.basebranch,
    )


def fill_config(config: RepoConfig) -> RepoConfig:
    """Prompts user for missing config values"""
    filled_config: dict[str, str] = {}
    for key, value in config._asdict().items():
        filled_config[key] = value if value else input(f"Enter {key}: ")
    return RepoConfig(**filled_config)


def all_files_exist(files: list[str]) -> bool:
    """Confirms files in list exist"""
    return all([pathlib.Path(file).exists() for file in files]) if files else False


def inject_env_secrets(config: RepoConfig) -> None:
    """Push required values to environ"""
    os.environ["GITHUB_AUTH_TOKEN"] = config.usertoken
    os.environ["GITHUB_USER_NAME"] = config.username


def create_pull_request(
    prompt_values: PromptValues,
    config: RepoConfig,
    filenames: list[str],
    draft: bool = False,
) -> str:
    """Create pull request with indicated files, returns url on success"""

    client = RepoActions(config.ownername, config.reponame)

    branch = client.create_branch(config.basebranch, prompt_values.new_branch)

    blobs = [client.create_blob(content).sha for content in load_files(filenames)]
    blob_names = [(sha, filename) for sha, filename in zip(blobs, filenames)]

    tree = client.create_blob_tree(branch.sha, blob_names)

    commit = client.create_commit(
        author_name=config.username,
        author_email=config.useremail,
        branch_sha=branch.sha,
        tree_sha=tree.sha,
        message=prompt_values.message,
    )

    client.update_reference(prompt_values.new_branch, commit.sha)

    pull_request = client.create_pull_request(
        new_branch=prompt_values.new_branch,
        base_branch=config.basebranch,
        pr_title=prompt_values.title,
        pr_body=prompt_values.message,
        draft=draft,
    )

    return pull_request.html_url


def load_files(filenames: list[str]) -> list[str]:
    """Loads files"""
    files: list[str] = []
    for filename in filenames:
        with open(filename, encoding="utf-8") as infile:
            files.append(infile.read())
    return files


if __name__ == "__main__":
    main_cli()
