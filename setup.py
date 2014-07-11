# -*- coding: utf-8 -*-
from setuptools import setup
from dotfiles import __version__


setup(
    name='dotfiles',
    version=__version__,
    author='Jon Bernard',
    author_email='jbernard@tuxion.com',
    url='https://github.com/jbernard/dotfiles',
    packages=['dotfiles'],
    description='Easily manage your dotfiles',
    long_description=open('README.rst').read() + '\n\n' +
                     open('LICENSE.rst').read() + '\n\n' +
                     open('HISTORY.rst').read(),
    entry_points = '''
        [console_scripts]
        dotfiles=dotfiles.cli:main
    ''',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: ISC License (ISCL)'
    ],
)
