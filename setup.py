#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from dotfiles.core import __version__


setup(name='dotfiles',
      version=__version__,
      description='Easily manage your dotfiles',
      long_description=open('README.rst').read(),
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
