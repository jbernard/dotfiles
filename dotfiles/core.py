# -*- coding: utf-8 -*-

"""
dotfiles.core
~~~~~~~~~~~~~

This module provides the basic functionality of dotfiles.
"""

import os
import shutil
import fnmatch


__version__ = '0.5.4'
__author__ = 'Jon Bernard'
__license__ = 'ISC'


class Dotfile(object):

    def __init__(self, name, target, home):
        if name.startswith('/'):
            self.name = name
        else:
            self.name = home + '/.%s' % name.lstrip('.')
        self.relpath = self.name[len(home)+1:]
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
                        % self.relpath)
                return
            if os.path.isdir(self.name) and not os.path.islink(self.name):
                shutil.rmtree(self.name)
            else:
                os.remove(self.name)
            os.symlink(self.target, self.name)

    def add(self):
        if self.status == 'missing':
            print("Skipping \"%s\", file not found" % self.relpath)
            return
        if self.status == '':
            print("Skipping \"%s\", already managed" % self.relpath)
            return

        target_dir = os.path.dirname(self.target)
        if not os.path.isdir(target_dir):
            os.makedirs(target_dir)
        shutil.move(self.name, self.target)
        os.symlink(self.target, self.name)

    def remove(self):
        if self.status != '':
            print("Skipping \"%s\", file is %s" % (self.relpath, self.status))
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

        all_repofiles = list()
        for root, dirs, files in os.walk(self.repository):
            for f in files:
                f_rel_path = os.path.join(root, f)[len(self.repository)+1:]
                all_repofiles.append(f_rel_path)
            for d in dirs:
                if d[0] == '.':
                    dirs.remove(d)
                    continue
                dotdir = self._home_fqpn(os.path.join(root, d))
                if os.path.islink(dotdir):
                    dirs.remove(d)
                    d_rel_path = os.path.join(root, d)[len(self.repository)+1:]
                    all_repofiles.append(d_rel_path)
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

    def _repo_fqpn(self, homepath):
        """Return the fully qualified path to a dotfile in the repository."""

        dotfile_rel_path = homepath[len(self.homedir)+1:]
        dotfile_rel_repopath = self.prefix\
                               + dotfile_rel_path[1:] # remove leading '.'
        return os.path.join(self.repository, dotfile_rel_repopath)

    def _home_fqpn(self, repopath):
        """Return the fully qualified path to a dotfile in the home dir."""

        dotfile_rel_path = repopath[len(self.repository)+1+len(self.prefix):]
        return os.path.join(self.homedir, '.%s' % dotfile_rel_path)

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
            if file[len(self.homedir)+1:].startswith('.'):
                getattr(Dotfile(file, self._repo_fqpn(file), self.homedir),
                        action)()
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
