from io import open
from os import path
from setuptools import setup, find_packages
from dotfiles import __version__

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf8') as f:
    long_description = f.read()

test_requirements = [
    'pytest',
    'pytest-pep8',
    'pytest-flakes',
]

setup(
    name='dotfiles',
    version=__version__,
    description='Easily manage your dotfiles',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/jbernard/dotfiles',
    author='Jon Bernard',
    author_email='jbernard@jbernard.io',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: ISC License (ISCL)'
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(),
    install_requires=['click'],
    setup_requires=['pytest-runner'],
    tests_require=test_requirements,
    entry_points={
        'console_scripts': [
            'dotfiles=dotfiles.cli:cli',
        ],
    },
    project_urls={
        'Bug Reports': 'https://github.com/jbernard/dotfiles/issues',
        'Source': 'https://github.com/jbernard/dotfiles',
    },
)
