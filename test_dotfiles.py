#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement

import os
import shutil
import tempfile
import unittest

from dotfiles import core
from dotfiles import cli
from dotfiles.utils import is_link_to


def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)


class DotfilesTestCase(unittest.TestCase):

    def setUp(self):
        """Create a temporary home directory."""

        self.homedir = tempfile.mkdtemp()

        # Create a repository for the tests to use.
        self.repository = os.path.join(self.homedir, 'Dotfiles')
        os.mkdir(self.repository)

    def tearDown(self):
        """Delete the temporary home directory and its contents."""

        shutil.rmtree(self.homedir)

    def assertPathEqual(self, path1, path2):
        self.assertEqual(
            os.path.realpath(path1),
            os.path.realpath(path2))

    def test_force_sync_directory(self):
        """Test forced sync when the dotfile is a directory.

        I installed the lastpass chrome extension which stores a socket in
        ~/.lastpass. So I added that directory as an external to /tmp and
        attempted a forced sync. An error occurred because sync() calls
        os.remove() as it mistakenly assumes the dotfile is a file and not
        a directory.
        """

        os.mkdir(os.path.join(self.homedir, '.lastpass'))
        externals = {'.lastpass': '/tmp'}

        dotfiles = core.Dotfiles(
                homedir=self.homedir, repository=self.repository,
                prefix='', ignore=[], externals=externals, packages=[],
                dry_run=False)

        dotfiles.sync(force=True)

        self.assertPathEqual(
                os.path.join(self.homedir, '.lastpass'),
                '/tmp')

    def test_dispatch(self):
        """Test that the force option is handed on to the sync method."""
        class MockDotfiles(object):
            def sync(self, files=None, force=False):
                assert bool(force)
        dotfiles = MockDotfiles()
        cli.dispatch(dotfiles, 'sync', True, [])

    def test_move_repository(self):
        """Test the move() method for a Dotfiles repository."""

        touch(os.path.join(self.repository, 'bashrc'))

        dotfiles = core.Dotfiles(
                homedir=self.homedir, repository=self.repository,
                prefix='', ignore=[], force=True, externals={}, packages=[],
                dry_run=False)

        dotfiles.sync()

        # Make sure sync() did the right thing.
        self.assertPathEqual(
                os.path.join(self.homedir, '.bashrc'),
                os.path.join(self.repository, 'bashrc'))

        target = os.path.join(self.homedir, 'MyDotfiles')

        dotfiles.move(target)

        self.assertTrue(os.path.exists(os.path.join(target, 'bashrc')))
        self.assertPathEqual(
                os.path.join(self.homedir, '.bashrc'),
                os.path.join(target, 'bashrc'))

    def test_force_sync_directory_symlink(self):
        """Test a forced sync on a directory symlink.

        A bug was reported where a user wanted to replace a dotfile repository
        with an other one. They had a .vim directory in their home directory
        which was obviously also a symbolic link. This caused:

        OSError: Cannot call rmtree on a symbolic link
        """

        # Create a dotfile symlink to some directory
        os.mkdir(os.path.join(self.homedir, 'vim'))
        os.symlink(os.path.join(self.homedir, 'vim'),
                   os.path.join(self.homedir, '.vim'))

        # Create a vim directory in the repository. This will cause the above
        # symlink to be overwritten on sync.
        os.mkdir(os.path.join(self.repository, 'vim'))

        # Make sure the symlink points to the correct location.
        self.assertPathEqual(
                os.path.join(self.homedir, '.vim'),
                os.path.join(self.homedir, 'vim'))

        dotfiles = core.Dotfiles(
                homedir=self.homedir, repository=self.repository,
                prefix='', ignore=[], externals={}, packages=[], dry_run=False)

        dotfiles.sync(force=True)

        # The symlink should now point to the directory in the repository.
        self.assertPathEqual(
                os.path.join(self.homedir, '.vim'),
                os.path.join(self.repository, 'vim'))

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
            touch(os.path.join(self.repository, original))

        dotfiles = core.Dotfiles(
                homedir=self.homedir, repository=self.repository,
                prefix='', ignore=ignore, externals={}, packages=[],
                dry_run=False)

        dotfiles.sync()

        # Now check that the files that should have a symlink
        # point to the correct file and are the only files that
        # exist in the home dir.
        self.assertEqual(
            sorted(os.listdir(self.homedir)),
            sorted([f[1] for f in all_dotfiles] + ['Dotfiles']))

        for original, symlink in all_dotfiles:
            self.assertPathEqual(
                os.path.join(self.repository, original),
                os.path.join(self.homedir, symlink))

    def test_packages(self):
        """
        Test packages.
        """
        files = ['foo', 'package/bar']
        symlinks = ['.foo', '.package/bar']
        join = os.path.join

        # Create files
        for filename in files:
            path = join(self.repository, filename)
            dirname = os.path.dirname(path)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            touch(path)

        # Create Dotfiles object
        dotfiles = core.Dotfiles(
                homedir=self.homedir, repository=self.repository,
                prefix='', ignore=[], externals={}, packages=['package'],
                dry_run=False)

        # Create symlinks in homedir
        dotfiles.sync()

        # Verify it created what we expect
        def check_all(files, symlinks):
            self.assertTrue(os.path.isdir(join(self.homedir, '.package')))
            for src, dst in zip(files, symlinks):
                self.assertTrue(is_link_to(join(self.homedir, dst),
                    join(self.repository, src)))
        check_all(files, symlinks)

        # Add files to the repository
        new_files = [join(self.homedir, f) for f in ['.bar', '.package/foo']]
        for filename in new_files:
            path = join(self.homedir, filename)
            touch(path)
        new_repo_files = ['bar', 'package/foo']
        dotfiles.add(new_files)
        check_all(files + new_repo_files, symlinks + new_files)

        # Remove them from the repository
        dotfiles.remove(new_files)
        check_all(files, symlinks)

        # Move the repository
        self.repository = join(self.homedir, 'Dotfiles2')
        dotfiles.move(self.repository)
        check_all(files, symlinks)

    def test_missing_package(self):
        """
        Test a non-existent package.
        """

        package_file = '.package/bar'

        # Create Dotfiles object
        dotfiles = core.Dotfiles(
                homedir=self.homedir, repository=self.repository,
                prefix='', ignore=[], externals={}, packages=['package'],
                dry_run=False)

        path = os.path.join(self.homedir, package_file)
        dirname = os.path.dirname(path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        touch(path)

        dotfiles.add([os.path.join(self.homedir, package_file)])


    def test_single_sync(self):
        """
        Test syncing a single file in the repo

        The following repo dir exists:

        bashrc
        netrc
        vimrc

        Syncing only vimrc should have the folowing sync result in home:

        .vimrc -> Dotfiles/vimrc

        """

        # define the repository contents
        repo_files = (
            ('bashrc', False),
            ('netrc',  False),
            ('vimrc',  True))

        # populate the repository
        for dotfile, _ in repo_files:
            touch(os.path.join(self.repository, dotfile))

        dotfiles = core.Dotfiles(
                homedir=self.homedir, repository=self.repository,
                prefix='', ignore=[], externals={}, packages=[],
                dry_run=False)

        # sync only certain dotfiles
        for dotfile, should_sync in repo_files:
            if should_sync:
                dotfiles.sync(files=['.%s' % dotfile])

        # verify home directory contents
        for dotfile, should_sync in repo_files:
            if should_sync:
                self.assertPathEqual(
                    os.path.join(self.repository, dotfile),
                    os.path.join(self.homedir, '.%s' % dotfile))
            else:
                self.assertFalse(os.path.exists(
                    os.path.join(self.homedir, dotfile)))


if __name__ == '__main__':
    unittest.main()
