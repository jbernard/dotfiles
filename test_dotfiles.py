#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement

import os
import shutil
import tempfile
import unittest

from dotfiles import core


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

    def verifyFileStatus(self, home_rel_path, host=None):
        homepath = os.path.join(self.homedir, home_rel_path)
        if host is None:
            repopath = os.path.join(self.repository, home_rel_path[1:])
        else:
            repopath = os.path.join(self.repository, '%s.host' % host,
                                    home_rel_path[1:])

        self.assertTrue(os.path.islink(homepath),
                        '%s is not a symlink' % homepath)
        self.assertTrue(not os.path.islink(repopath))
        self.assertTrue(os.path.isfile(repopath),
                        '%s does not exist (in repo)' % repopath)
        self.assertPathEqual(homepath, repopath)

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
                prefix='', ignore=[], externals=externals)

        dotfiles.sync(force=True)

        self.assertPathEqual(
                os.path.join(self.homedir, '.lastpass'),
                '/tmp')

    def test_move_repository(self):
        """Test the move() method for a Dotfiles repository."""

        touch(os.path.join(self.repository, 'bashrc'))

        dotfiles = core.Dotfiles(
                homedir=self.homedir, repository=self.repository,
                prefix='', ignore=[], force=True, externals={})

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
                prefix='', ignore=[], externals={})

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
                prefix='', ignore=ignore, externals={})

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

    def test_dotdir_file_add_sync_remove(self):
        """Test that is is possible to add files in dot-directories
        and that they are managed correctly.

        This is especially usefull for applications that mix state files and
        configuration files in their dot-directory, for instance :
            - .unison which contains *prf and state files
            - .lftp which contains rc (conf file) and log, cwd_history.
        """
        os.mkdir(os.path.join(self.homedir, '.unison'))
        os.mkdir(os.path.join(self.homedir, '.lftp'))
        all_repo_files = (
            ('.vimrc', True),
            ('.unison/home.prf', True),
            ('.unison/are8d491ed362b0a4cf3e8d77ef3e08a1c', False),
            ('.unison/fpe8d491ed362b0a4cf3e8d77ef3e08a1c', False),
            ('.lftp/log', False),
            ('.lftp/rc', True),
            ('.lftp/cwd_history', False),
        )
        repo_dir = '.ikiwiki'

        for homefile, in_repository in all_repo_files:
            touch(os.path.join(self.homedir, homefile))
        os.mkdir(os.path.join(self.homedir, repo_dir))

        dotfiles = core.Dotfiles(homedir=self.homedir,
                                 repository=self.repository,
                                 prefix='', ignore=[], externals={})

        dotfiles.add([os.path.join(self.homedir, homefile)
                      for homefile, in_repo in all_repo_files
                      if in_repo])
        for homefile, in_repository in all_repo_files:
            if in_repository:
                self.verifyFileStatus(homefile)

            for dotdir in ('.unison', '.lftp'):
                homepath = os.path.join(self.homedir, dotdir)
                self.assertTrue(not os.path.islink(homepath))
                self.assertTrue(os.path.isdir(homepath))

        os.unlink(os.path.join(self.homedir, '.vimrc'))
        os.unlink(os.path.join(self.homedir, '.lftp/rc'))

        os.unlink(os.path.join(self.homedir, '.unison/home.prf'))
        touch(os.path.join(self.homedir, '.unison/home.prf'))

        dotfiles._load() # refresh file states
        dotfiles.sync()
        for homefile in ('.vimrc', '.lftp/rc'):
            self.verifyFileStatus(homefile)
        self.assertTrue(not os.path.islink(os.path.join(self.homedir,
                                                        '.unison/home.prf')))
        self.assertTrue(os.path.isfile(os.path.join(self.homedir,
                                       '.unison/home.prf')))

        dotfiles._load() # refresh file states
        dotfiles.sync(force=True)
        self.verifyFileStatus('.unison/home.prf')

        dotfiles.remove([os.path.join(self.homedir, '.lftp/rc')])
        self.assertTrue(not os.path.islink(os.path.join(self.homedir,
                                                        '.lftp/rc')))
        self.assertTrue(os.path.isfile(os.path.join(self.homedir, '.lftp/rc')))

    def test_hosts_mode(self):
        """Test that host mode behaves correctly."""

        all_repo_files = (
            ('.vimrc', 'all'),
            ('.mozilla', 'guiworkstation'),
        )

        for homefile, host in all_repo_files:
            touch(os.path.join(self.homedir, homefile))

        os.makedirs(os.path.join(self.homedir, self.repository, 'all.host'))

        dotfiles = core.Dotfiles(homedir=self.homedir,
                                 repository=self.repository,
                                 prefix='', ignore=[], externals={})
        self.assertTrue(dotfiles.hosts_mode())

        for homefile, host in all_repo_files:
            dotfiles.add([os.path.join(self.homedir, homefile)], host)
            self.verifyFileStatus(homefile, host)

        for homefile, host in all_repo_files:
            os.unlink(os.path.join(self.homedir, homefile))

        dotfiles._load()
        dotfiles.sync()
        self.verifyFileStatus('.vimrc', 'all')
        self.assertTrue(not os.path.exists(os.path.join(self.homedir, '.mozilla')))

        dotfiles._load()
        dotfiles.sync(hostname='guiworkstation')
        self.assertTrue(os.path.exists(os.path.join(self.homedir, '.mozilla')))

        dotfiles._load()
        dotfiles.remove([os.path.join(self.homedir, '.mozilla')],
                        'guiworkstation')

        dotfiles._load()
        dotfiles.sync(hostname='guiworkstation')
        self.verifyFileStatus('.vimrc', 'all')
        self.assertTrue(not os.path.islink(os.path.join(self.homedir, '.mozilla')))


def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(DotfilesTestCase)
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
