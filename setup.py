# -*- coding: utf-8 -*-
""" Setup Script """
from setuptools import setup  # type: ignore
from setuptools import find_packages  # type: ignore

setup(
    name="preocts_github_client",
    version="0.1.0",
    description="Create branch, add file, and make pull request using Github API",
    author="Preocts",
    author_email="preocts@preocts.com",
    url="https://github.com/Preocts/gitclient",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=[],
)
