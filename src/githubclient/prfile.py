"""
CLI Controls for creates a PR with a file

All commands can be given 'global'

Commands:
    --reponame
    --ownername
    --username
    --useremail
    --usertoken

Author: Preocts <Preocts#8196>
"""
from __future__ import annotations

import argparse
import pathlib
import sys
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import MutableMapping
from typing import NamedTuple
from typing import Optional
from typing import Sequence

import colorama
import toml
from colorama import Fore

REPO_URL = "https://github.com/Preocts/githubclient"
CONFIG_FILE = ".default_config.toml"
CWD = pathlib.Path.cwd()
DEFAULT_NEW_BRANCH = datetime.now().isoformat()
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

    def to_toml(self) -> Dict[str, Any]:
        """Returns config as nested dict under key: repo"""
        return {"repo": self._asdict()}

    @classmethod
    def from_toml(cls, toml_in: MutableMapping[str, Any]) -> RepoConfig:
        """Generate class from toml load"""
        repo = toml_in.get("repo", {})
        return cls(
            reponame=repo.get("reponame", ""),
            ownername=repo.get("ownername", ""),
            username=repo.get("username", ""),
            useremail=repo.get("useremail", ""),
            usertoken=repo.get("usertoken", ""),
        )


def cli_parser(args: Optional[Sequence[str]] = None) -> argparse.Namespace:
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
        "--usertoken",
        type=str,
        help="Set the developer auth-token (must have 'public_repo' access)",
    )
    return parser.parse_args() if args is None else parser.parse_args(args)


def main(args: argparse.Namespace) -> int:
    """Main CLI process"""
    config = fill_config(load_config(CONFIG_FILE, args))
    save_config(CONFIG_FILE, config)

    if not all_files_exist(args.filenames):
        raise FileNotFoundError(f"Unable to find files: {args.filenames}")

    prompt_values = run_user_prompt()

    print(prompt_values)

    return 0


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
        print(f"\n{Fore.GREEN}New Branch: {Fore.WHITE}{new_branch}")
        print(f"{Fore.GREEN}PR Title  : {Fore.WHITE}{title}")
        print(f"{Fore.GREEN}PR Message: {Fore.WHITE}{message}")
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
    """Save toml config in the working directory"""
    with open(pathlib.Path(CWD / filename), "w") as toml_out:
        toml.dump(config.to_toml(), toml_out)


def load_config(filename: str, args: argparse.Namespace) -> RepoConfig:
    """Load config toml, merge with and CLI optionals"""
    try:
        with open(pathlib.Path(CWD / filename), "r") as toml_in:
            config = RepoConfig.from_toml(toml.load(toml_in))
    except FileNotFoundError:
        config = RepoConfig()

    return RepoConfig(
        reponame=config.reponame if args.reponame is None else args.reponame,
        ownername=config.ownername if args.ownername is None else args.ownername,
        username=config.username if args.username is None else args.username,
        useremail=config.useremail if args.useremail is None else args.useremail,
        usertoken=config.usertoken if args.usertoken is None else args.usertoken,
    )


def fill_config(config: RepoConfig) -> RepoConfig:
    """Prompts user for missing config values"""
    filled_config: Dict[str, str] = {}
    for key, value in config._asdict().items():
        filled_config[key] = value if value else input(f"Enter {key}: ")

    return RepoConfig(**filled_config)


def all_files_exist(files: List[str]) -> bool:
    """Confirms files in list exist"""
    return all([pathlib.Path(file).exists() for file in files]) if files else False


if __name__ == "__main__":
    colorama.init(autoreset=True)
    sys.exit(main(cli_parser()))
