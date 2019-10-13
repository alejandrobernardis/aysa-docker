# Author: Alejandro M. Bernardis
# Email: alejandro.bernardis at gmail.com
# Created: 2019/10/12
# ~

import aysa
from setuptools import setup, find_packages
from os import path
from io import open

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'readme.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name=aysa.__title__,
    version=aysa.__version__,
    description=aysa.__summary__,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url=aysa.__uri__,
    author=aysa.__author__,
    author_email=aysa.__email__,
    keywords='docker registry services development',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    python_requires='>=3.6.*, <4',

    # TODO(0608156): crear un archivo requirements.txt con pipenv.
    install_requires=[],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],

    entry_points={
        'console_scripts': [
            'aysa=aysa.docker.cli:main',
        ],
    },

    project_urls={
        'Bug Reports': aysa.__issues__,
        'Source': aysa.__uri__,
    },
)