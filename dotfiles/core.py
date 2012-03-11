# -*- coding: utf-8 -*-

"""
dotfiles.core
~~~~~~~~~~~~~

This module provides the basic functionality of dotfiles.
"""

import os
import shutil
import fnmatch


__version__ = '0.5.3'
__author__ = 'Jon Bernard'
__license__ = 'ISC'


class Dotfile(object):

    def __init__(self, name, target, home):
        if name.startswith('/'):
            self.name = name
        else:
            self.name = home + '/.%s' % name.strip('.')
        self.basename = os.path.basename(self.name)
        self.target = target.rstrip('/')
        self.status = ''
        if not os.path.lexists(self.name):
            self.status = 'missing'
        elif os.path.realpath(self.name) != self.target:
            self.status = 'unsynced'

    def sync(self, force):
        if self.status == 'missing':
            os.symlink(self.target, self.name)
        elif self.status == 'unsynced':
            if not force:
                print("Skipping \"%s\", use --force to override"
                        % self.basename)
                return
            if os.path.isdir(self.name) and not os.path.islink(self.name):
                shutil.rmtree(self.name)
            else:
                os.remove(self.name)
            os.symlink(self.target, self.name)

    def add(self):
        if self.status == 'missing':
            print("Skipping \"%s\", file not found" % self.basename)
            return
        if self.status == '':
            print("Skipping \"%s\", already managed" % self.basename)
            return
        shutil.move(self.name, self.target)
        os.symlink(self.target, self.name)

    def remove(self):
        if self.status != '':
            print("Skipping \"%s\", file is %s" % (self.basename, self.status))
            return
        os.remove(self.name)
        shutil.move(self.target, self.name)

    def __str__(self):
        return '%-18s %-s' % (self.name.split('/')[-1], self.status)


class Dotfiles(object):
    """A Dotfiles Repository."""

    __attrs__ = ['homedir', 'repository', 'prefix', 'ignore', 'externals']

    def __init__(self, **kwargs):

        # Map args from kwargs to instance-local variables
        for k, v in kwargs.items():
            if k in self.__attrs__:
                setattr(self, k, v)

        self._load()

    def _load(self):
        """Load each dotfile in the repository."""

        self.dotfiles = list()

        all_repofiles = os.listdir(self.repository)
        repofiles_to_symlink = set(all_repofiles)

        for pat in self.ignore:
            repofiles_to_symlink.difference_update(
                    fnmatch.filter(all_repofiles, pat))

        for dotfile in repofiles_to_symlink:
            self.dotfiles.append(Dotfile(dotfile[len(self.prefix):],
                os.path.join(self.repository, dotfile), self.homedir))

        for dotfile in self.externals.keys():
            self.dotfiles.append(Dotfile(dotfile,
                os.path.expanduser(self.externals[dotfile]),
                self.homedir))

    def _fqpn(self, dotfile):
        """Return the fully qualified path to a dotfile."""

        return os.path.join(self.repository,
                            self.prefix + os.path.basename(dotfile).strip('.'))

    def list(self, verbose=True):
        """List the contents of this repository."""

        for dotfile in sorted(self.dotfiles, key=lambda dotfile: dotfile.name):
            if dotfile.status or verbose:
                print(dotfile)

    def check(self):
        """List only unsynced and/or missing dotfiles."""

        self.list(verbose=False)

    def sync(self, force=False):

        """Synchronize this repository, creating and updating the necessary
        symbolic links."""

        for dotfile in self.dotfiles:
            dotfile.sync(force)

    def add(self, files):
        """Add dotfile(s) to the repository."""

        self._perform_action('add', files)

    def remove(self, files):
        """Remove dotfile(s) from the repository."""

        self._perform_action('remove', files)

    def _perform_action(self, action, files):
        for file in files:
            file = file.rstrip('/')
            if os.path.basename(file).startswith('.'):
                getattr(Dotfile(file, self._fqpn(file), self.homedir), action)()
            else:
                print("Skipping \"%s\", not a dotfile" % file)

    def move(self, target):
        """Move the repository to another location."""

        if os.path.exists(target):
            raise ValueError('Target already exists: %s' % (target))

        shutil.copytree(self.repository, target)
        shutil.rmtree(self.repository)

        self.repository = target

        self._load()
        self.sync(force=True)
