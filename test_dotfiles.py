#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import tempfile
import unittest

from dotfiles import core


def touch(fname, times=None):
    with file(fname, 'a'):
        os.utime(fname, times)


class DotfilesTestCase(unittest.TestCase):

    def setUp(self):
        """Create a temporary home directory."""

        self.home = tempfile.mkdtemp()

        # Create a repository for the tests to use.
        self.repo = os.path.join(self.home, 'Dotfiles')
        os.mkdir(self.repo)

    def tearDown(self):
        """Delete the temporary home directory and its contents."""

        shutil.rmtree(self.home)

    def test_force_sync_directory(self):
        """Test forced sync when the dotfile is a directory.

        I installed the lastpass chrome extension which stores a socket in
        ~/.lastpass. So I added that directory as an external to /tmp and
        attempted a forced sync. An error occurred because sync() calls
        os.remove() as it mistakenly assumes the dotfile is a file and not
        a directory.
        """

        os.mkdir(os.path.join(self.home, '.lastpass'))
        externals = {'.lastpass': '/tmp'}

        dotfiles = core.Dotfiles(home=self.home, repo=self.repo, prefix='',
                                ignore=[], externals=externals)

        dotfiles.sync(force=True)

        self.assertEqual(
                os.path.realpath(os.path.join(self.home, '.lastpass')),
                os.path.realpath('/tmp'))

    def test_move_repository(self):
        """Test the move() method for a Dotfiles repository."""

        touch(os.path.join(self.repo, 'bashrc'))

        dotfiles = core.Dotfiles(
                home=self.home, repo=self.repo, prefix='',
                ignore=[], force=True, externals={})

        dotfiles.sync()

        # Make sure sync() did the right thing.
        self.assertEqual(
                os.path.realpath(os.path.join(self.home, '.bashrc')),
                os.path.realpath(os.path.join(self.repo, 'bashrc')))

        target = os.path.join(self.home, 'MyDotfiles')

        dotfiles.move(target)

        self.assertTrue(os.path.exists(os.path.join(target, 'bashrc')))
        self.assertEqual(
                os.path.realpath(os.path.join(self.home, '.bashrc')),
                os.path.realpath(os.path.join(target, 'bashrc')))

    def test_sync_unmanaged_directory_symlink(self):
        """Test a forced sync on a directory symlink.

        A bug was reported where a user wanted to replace a dotfile repository
        with an other one. They had a .vim directory in their home directory
        which was obviously also a symbolic link. This caused:

        OSError: Cannot call rmtree on a symbolic link
        """

        # Create a dotfile symlink to some directory
        os.mkdir(os.path.join(self.home, 'vim'))
        os.symlink(os.path.join(self.home, 'vim'),
                   os.path.join(self.home, '.vim'))

        # Create a vim directory in the repository. This will cause the above
        # symlink to be overwritten on sync.
        os.mkdir(os.path.join(self.repo, 'vim'))

        # Make sure the symlink points to the correct location.
        self.assertEqual(
                os.path.realpath(os.path.join(self.home, '.vim')),
                os.path.realpath(os.path.join(self.home, 'vim')))

        dotfiles = core.Dotfiles(
                home=self.home, repo=self.repo, prefix='',
                ignore=[], externals={})

        dotfiles.sync(force=True)

        # The symlink should now point to the directory in the repository.
        self.assertEqual(
                os.path.realpath(os.path.join(self.home, '.vim')),
                os.path.realpath(os.path.join(self.repo, 'vim')))

    def test_glob_ignore_pattern(self):
        """ Test that the use of glob pattern matching works in the ignores list.

        The following repo dir exists:

        myscript.py
        myscript.pyc
        myscript.pyo
        bashrc
        bashrc.swp
        vimrc
        vimrc.swp
        install.sh

        Using the glob pattern dotfiles should have the following sync result in home:

        .myscript.py -> Dotfiles/myscript.py
        .bashrc -> Dotfiles/bashrc
        .vimrc -> Dotfiles/vimrc

        """
        ignore = ['*.swp', '*.py?', 'install.sh']

        all_repo_files = (
            ('myscript.py', '.myscript.py'),
            ('myscript.pyc', None),
            ('myscript.pyo', None),
            ('bashrc', '.bashrc'),
            ('bashrc.swp', None),
            ('vimrc', '.vimrc'),
            ('vimrc.swp', None),
            ('install.sh', None)
        )

        all_dotfiles = [f for f in all_repo_files if f[1] is not None]

        for original, symlink in all_repo_files:
            touch(os.path.join(self.repo, original))

        dotfiles = core.Dotfiles(
                home=self.home, repo=self.repo, prefix='',
                ignore=ignore, externals={})

        dotfiles.sync()

        # Now check that the files that should have a symlink
        # point to the correct file and are the only files that
        # exist in the home dir.
        self.assertEqual(
            sorted(os.listdir(self.home)),
            sorted([f[1] for f in all_dotfiles] + ['Dotfiles']))

        for original, symlink in all_dotfiles:
            original_path = os.path.join(self.repo, original)
            symlink_path = os.path.join(self.home, symlink)

            self.assertEqual(
                os.path.realpath(original_path),
                os.path.realpath(symlink_path))


def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(DotfilesTestCase)
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
