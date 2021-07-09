# -*- coding: utf-8 -*-
"""
A sample use of the gitclient class

NOTE: Before running this code follow setup guide below

This requires you to set four (4) globals with your GitHub information
which are found below.

You will also need a personal OAuth token from GitHub. If the target
repo is public (recommended) the only permission your personal token
requires is 'public_repo'

Set an enviromental var named 'GITCLIENT_OAUTH' with your personal token.
    bash:
    $ export GITCLIENT_OAUTH="[YOUR TOKEN]"

    command prompt/powershell:
    $ SET GITCLIENT_OAUTH="[YOUR TOKEN]"

To run from root of project:
    $ python3 -m example.sample
"""
import logging
import os

from githubclient.gitclient import FileObj
from githubclient.gitclient import GitClient

logger = logging.getLogger(__name__)

# Set these to your information
OWNER = "[REPO OWNER]"  # 'github.com/[OWNER]/[REPONAME]'
REPO = "[REPO NAME]"
NAME = "[YOUR GITHUB NAME]"
EMAIL = "[YOUR GITHUB ACCOUNT EMAIL]"


def main() -> None:
    """Simple sample of the class"""
    logging.basicConfig(level="DEBUG")
    # Load your github access token to an environment variable "GITCLIENT_OAUTH"
    token = os.getenv("GITCLIENT_OAUTH", "")

    if not token:
        logger.critical("Set a GITCLIENT_OAUTH, read the code Luke.")
        return

    file01 = open("./example/sample_doc01.md", "r").read()
    file02 = open("./example/sample_doc02.md", "r").read()

    files_to_add = [
        FileObj(file01, "my_sample.md"),
        FileObj(file02, "path_sample.md", "new_path/"),
    ]

    client = GitClient(
        owner=OWNER,
        repo=REPO,
        oauth=token,
    )

    if not client.create_branch("main", "sample_branch"):
        logger.critical("Failed to create branch!")
        return

    if not client.add_files(files_to_add):
        logger.critical("Failed to add files!")
        return

    if not client.create_commit(NAME, EMAIL):
        logger.critical("Failed to make commit!")
        return

    if not client.create_pull("main", "Auto PR by Python", "# Happy Pandas"):
        logger.critical("Failed to make pull request!")

    client.apply_labels(["New", "Pandas", "Happy"])

    print("\n\nIf you are reading this then everthing ran as expected.")
    print("You should go confirm in GitHub!")


if __name__ == "__main__":
    main()
