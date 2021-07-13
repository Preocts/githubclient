[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Preocts/python-template/main.svg)](https://results.pre-commit.ci/latest/github/Preocts/githubclient/main)
[![Python package](https://github.com/Preocts/githubclient/actions/workflows/python-tests.yml/badge.svg?branch=main)](https://github.com/Preocts/githubclient/actions/workflows/python-tests.yml)

# Create branch, add file, and make pull request using GitHub API

**Current Activity**
- [x] Metrics capture to debug console
- [~] Rewrite API layer (we are here)
- [_] Refactor client class to use API layer
- [_] Add CLI interface
  - [_] Send to repo as Pull Request
  - [_] Send to gist (create/update)

---

Automation class to accomplish the following in GitHub:
1. Create a new branch
1. Upload a given text file
1. Commit the file to the branch
1. Create a pull request

## [Read the write-up here](docs/write-up.md)

---

### Requires
- Python 3.8

---

### Example Usage

**See example file**: [example/sample.py](example/sample.py)

### Notes

If the branch already exists the logs will throw a `422` error. However, the class will attempt to recover the needed `sha` of the existing branch and carry on with the process.

If a pull request already exists for the branch another `422` error will be throw in the logs. The class will attempt to look up the existing pull request number and continue with applying tags.

The process is designed to fall-through with errors, returning a `False` boolean value if something beyond the two listed errors occurred during the attempt.

---

### Installation

*NOTE: All instructions are using bash as the shell. It is recommended that you use a virtual environment such as `venv` to maintain libraries.*

**Using pip to install from GitHub**
```bash
# Specific tag version (replace ? with desired tag)
$ pip install git://github.com/preocts/gitclient.git@v?.?.?

# Most recent commit to main (unstable)
$ pip install git://github.com/preocts/gitclient.git
```

---

## Local developer installation

It is **highly** recommended to use a `venv` for installation. Leveraging a `venv` will ensure the installed dependency files will not impact other python projects or system level requirements.

Clone this repo and enter root directory of repo:
```bash
$ git clone https://github.com/Preocts/[MODULE_NAME]
$ cd [MODULE_NAME]
```

Create and activate `venv`:
```bash
$ python3 -m venv venv
$ . venv/bin/activate
```

Your command prompt should now have a `(venv)` prefix on it.

Install editable library and development requirements:
```bash
(venv) $ pip install -r requirements-dev.txt
(venv) $ pip install --editable .
```

Install pre-commit hooks to local repo:
```bash
(venv) $ pre-commit install
```

Run tests
```bash
(venv) $ tox
```

To exit the `venv`:
```bash
(venv) $ deactivate
```

---

### Makefile

This repo has a Makefile with some quality of life scripts if your system supports `make`.

- `update` : Clean all artifacts, update pip, update requirements, install everything
- `clean-pyc` : Deletes python/mypy artifacts
- `clean-tests` : Deletes tox, coverage, and pytest artifacts
- `build-dist` : Build source distribution and wheel distribution
- `stats` : Shows line counts of `*.py` code
