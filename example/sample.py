# -*- coding: utf-8 -*-
""" A sample use of the gitclient class """
import os
import logging

from githubclient.gitclient import GitClient


def main() -> None:
    """ Simple sample of the class """
    logging.basicConfig(level="DEBUG")
    # Load your github access token to an environment variable "GITCLIENT_OAUTH"
    token = os.getenv("GITCLIENT_OAUTH", "")

    if not token:
        print("You need to set your personal access token, read the code Luke.")
        return

    # Create the client instance, providing your authentication information
    client = GitClient(
        name="[YOUR GITHUB NAME]",
        email="[YOUR GITHUB EMAIL]",
        owner="[TARGET REPO OWNER (probably your name)]",
        repo="[TARGET REPO]",
        oauth=token,
    )

    # Run the full process
    result = client.send_template(
        base_branch="main",
        new_branch="this_is_a_new_branch",
        file_name="new_file.md",
        file_contents="# Happy pandas\n\nThis can be any utf-8 text desired",
        pr_title="This is a sample PR",
        pr_content="All handled through automation.",
        labels=["New"],
    )

    if result:
        print("\n\nEverything ran as expected. Confirm in GitHub!")
    else:
        print("\n\nSomething went wrong. Check the logs for clues.")


if __name__ == "__main__":
    main()
