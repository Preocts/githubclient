[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Preocts/python-template/main.svg)](https://results.pre-commit.ci/latest/github/Preocts/githubclient/main)
[![Python package](https://github.com/Preocts/githubclient/actions/workflows/python-tests.yml/badge.svg?branch=main)](https://github.com/Preocts/githubclient/actions/workflows/python-tests.yml)

# Submit text files to a target repo as a pull request on new branch

**Current Activity**
- [x] Metrics capture to debug console
- [x] Rewrite API layer (we are here)
- [x] Refactor client class to use API layer
- [~] Create pip installable layer
- [~] Add CLI interface
  - [x] Send to repo as Pull Request
  - [_] Send to gist (create/update)
- [_] Update installation and usage documentation
- [_] Rename project

---

## What is this project?

[Read the write-up here](docs/write-up.md)

---

### Requires
- Python >= 3.7
- urllib3

---

### Installation

*pending*

---

## Local developer installation

It is **highly** recommended to use a `venv` for installation. Leveraging a `venv` will ensure the installed dependency files will not impact other python projects or system level requirements.

Clone this repo and enter root directory of repo:
```bash
$ git clone https://github.com/Preocts/githubclient
$ cd githubclient
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
