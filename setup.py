#!/usr/bin/env python
from setuptools import setup

def readme():
    with open('readme.md') as f:
        return f.read()

setup(
    name="testing",
    version="0.0.2",
    description="",
    long_description=readme(),
    url="http://github.com/xaedes/testing",
    author="xaedes",
    author_email="xaedes@gmail.com",
    license="MIT",
    packages=["testing"],
    tests_require=["pytest"], # invoke with setup.py pytest
    install_requires=[
        "funcy","numpy","pytest-runner"
    ],
    include_package_data=True,
    zip_safe=False
    )

