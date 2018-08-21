#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name="factsd",
    version="0.0.1",
    description="the facts daemon",
    author="Tris Emmy Wilson",
    author_email="anemptystring@gmail.com",
    packages=find_packages(),
    install_requires=["flask", "peewee", "click"],
    entry_points={"console_scripts": ["factsd = factsd.cli:base"]},
    include_package_data=True,
    zip_safe=False,
)
