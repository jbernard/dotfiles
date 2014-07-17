import os
import pytest
from utils import HomeDirectory
from dotfiles.core import Dotfiles as Repository


REPOSITORY = 'dotfiles'


def test_sync(tmpdir):
    """the quick, brown fox jumps over the lazy dog.

    lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
    tempor incididunt ut labore et dolore magna aliqua. ut enim ad minim veniam,
    quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
    consequat. duis aute irure dolor in reprehenderit in voluptate velit esse
    cillum dolore eu fugiat nulla pariatur. excepteur sint occaecat cupidatat
    non proident, sunt in culpa qui officia deserunt mollit anim id est
    laborum"""

    contents = {'.foo': True,
                '.bar': True,
                '.baz': False}

    homedir = HomeDirectory(str(tmpdir), REPOSITORY, contents)

    Repository(homedir=homedir.path,
               repository=os.path.join(homedir.path, REPOSITORY),
               prefix='', ignore=[], externals={}, packages=[],
               dry_run = False).sync()

    # .baz should now exist and link to the correct location
    contents['.baz'] = True
    homedir.verify(contents)
