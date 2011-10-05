#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from dotfiles.core import __version__


if sys.argv[-1] == "publish":
    os.system("python setup.py sdist upload")
    sys.exit()


if sys.argv[-1] == "test":
    os.system("python test_dotfiles.py")
    sys.exit()


setup(name='dotfiles',
      version=__version__,
      description='Easily manage your dotfiles',
      long_description=open('README.rst').read() + '\n\n' +
                       open('HISTORY.rst').read(),
      author='Jon Bernard',
      author_email='jbernard@tuxion.com',
      url='https://github.com/jbernard/dotfiles',
      packages=['dotfiles'],
      license='GPL',
      classifiers=(
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Natural Language :: English',
          'Programming Language :: Python',
      ),
      scripts=['bin/dotfiles'],
)
