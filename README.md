# Create branch, add file, and make pull request using GitHub API

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


Automation class to accomplish the following in GitHub:
1. Create a new branch
1. Upload a given text file
1. Commit the file to the branch
1. Create a pull request

## [Read the write-up here](docs/write-up.md)

---

### Requires
- Python 3.8

### Installation

*NOTE: All instructions are using bash as the shell. It is recommended that you use a virtual environment such as `venv` to maintain libraries.*

**Using pip to install from GitHub**
```bash
# Specific tag version
$ pip install git://github.com/preocts/gitclient.git@v0.1.0

# Most recent commit to main
$ pip install git://github.com/preocts/gitclient.git
```

**Cloning repo and installing with a local editable**
```bash
$ git clone https://github.com/Preocts/gitclient.git

$ make install

# For development linters and pre-commit
$ make install-dev
```

---

### Example Usage

```python
Usage:
    from githubclient.gitclient import GitClient

    ...
    # Code to load/create template file as string, utf-8
    ...

    client = GitClient(
        name="YOUR GITHUB NAME",
        email="ASSOCIATED EMAIL",
        owner="REPO-OWNER",  # (github.com/[OWNER]/[REPONAME])
        repo="REPO-NAME",
        oauth="[OAuth Secret Token]",
    )
    client.send_template(
        base_branch="main",
        new_branch="my_cool_branch,
        file_name="cool_template_file.md",
        file_contents="# Hello World",
        pr_title="Pull request Title",
        pr_content="Pull request message",
    )
```
