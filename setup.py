#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 25 14:39:37 2023

@author: villa
"""
from setuptools import setup, find_namespace_packages

with open("README.md") as file:
    long_description = file.read()

setup(
    name='defy',
    version='1.0.0',
    author='Lorenzo Villa',
    description='',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_namespace_packages(exclude=["defy.*.tests",
    					      "defy.*.*.tests",
    					      "defy.*.*.*.tests"]),
    install_requires=[
        'ase',
        'pymatgen>=2023.3.23',
        'pymatgen-analysis-defects>=2023.3.25',       
    ],
    extra_requires={'test':'pytest'},
    # entry_points={
    # "console_scripts": [
    #     "pynter = pynter.cli.main:main"]}
)


