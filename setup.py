import os
from setuptools import setup

THIS_DIR = os.path.abspath(os.path.dirname(__file__))

setup(
    name = 'htmap',
    version = '0.1.0',
    author = 'Josh Karpel',
    author_email = 'josh.karpel@gmail.com',
    description = '',
    long_description = open('README.md').read(),
    long_description_content_type = "text/markdown",
    url = 'https://github.com/htcondor/htmap',
    classifiers = [
    ],
    packages = [
        'snarl',
    ],
    install_requires = [
    ],
)
