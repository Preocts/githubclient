# -*- coding: utf-8 -*-
""" A sample use of the gitclient class """
import os
import logging

from githubclient.gitclient import GitClient  # type: ignore


def main() -> None:
    """ Simple sample of the class """
    logging.basicConfig(level="DEBUG")
    # Load your github access token to an environment variable "GITCLIENT_OAUTH"
    token = os.getenv("GITCLIENT_OAUTH", "")

    if not token:
        print("You need to set your personal access token, read the code Luke.")
        return

    client = GitClient(
        "[YOUR GITHUB NAME]",
        "[YOUR GITHUB EMAIL]",
        "[TARGET REPO OWNER (probably your name)]",
        "[TARGET REPO]",
        token,
    )

    result = client.send_template(
        "main",
        "this_is_a_new_branch",
        "new_file.md",
        "# Happy pandas",
        pr_title="This is a sample PR",
        pr_content="All handled through automation.",
        labels=["New"],
    )

    print(f"\n\nFinal status: {result}")


if __name__ == "__main__":
    main()
