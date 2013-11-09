# -*- coding: utf-8 -*-

"""
dotfiles.core
~~~~~~~~~~~~~

This module provides the basic functionality of dotfiles.
"""

import os
import os.path
import shutil
import fnmatch

from dotfiles.utils import realpath_expanduser, is_link_to
from dotfiles.compat import symlink


__version__ = '0.6.2'
__author__ = 'Jon Bernard'
__license__ = 'ISC'


class Dotfile(object):

    def __init__(self, name, target, home, add_dot=True, dry_run=False):
        if name.startswith('/'):
            self.name = name
        else:
            if add_dot:
                self.name = os.path.join(home, '.%s' % name.strip('.'))
            else:
                self.name = os.path.join(home, name)
        self.basename = os.path.basename(self.name)
        self.target = target.rstrip('/')
        self.dry_run = dry_run
        self.status = ''
        if not os.path.lexists(self.name):
            self.status = 'missing'
        elif not is_link_to(self.name, self.target):
            self.status = 'unsynced'

    def _symlink(self, target, name):
        if not self.dry_run:
            dirname = os.path.dirname(name)
            if not os.path.isdir(dirname):
                os.makedirs(dirname)
            symlink(target, name)
        else:
            print("Creating symlink %s => %s" % (target, name))

    def _rmtree(self, path):
        if not self.dry_run:
            shutil.rmtree(path)
        else:
            print("Removing %s and everything under it" % path)

    def _remove(self, path):
        if not self.dry_run:
            os.remove(path)
        else:
            print("Removing %s" % path)

    def _move(self, src, dst):
        if not self.dry_run:
            shutil.move(src, dst)
        else:
            print("Moving %s => %s" % (src, dst))

    def sync(self, force):
        if self.status == 'missing':
            self._symlink(self.target, self.name)
        elif self.status == 'unsynced':
            if not force:
                print("Skipping \"%s\", use --force to override"
                        % self.basename)
                return
            if os.path.isdir(self.name) and not os.path.islink(self.name):
                self._rmtree(self.name)
            else:
                self._remove(self.name)
            self._symlink(self.target, self.name)

    def add(self):
        if self.status == 'missing':
            print("Skipping \"%s\", file not found" % self.basename)
            return
        if self.status == '':
            print("Skipping \"%s\", already managed" % self.basename)
            return
        self._move(self.name, self.target)
        self._symlink(self.target, self.name)

    def remove(self):
        if self.status != '':
            print("Skipping \"%s\", file is %s" % (self.basename, self.status))
            return
        self._remove(self.name)
        self._move(self.target, self.name)

    def __str__(self):
        user_home = os.environ['HOME']
        common_prefix = os.path.commonprefix([user_home, self.name])
        if common_prefix:
            name = '~%s' % self.name[len(common_prefix):]
        else:
            name = self.name
        return '%-18s %-s' % (name, self.status)


class Dotfiles(object):
    """A Dotfiles Repository."""

    __attrs__ = ['homedir', 'repository', 'prefix', 'ignore', 'externals',
            'packages', 'dry_run']

    def __init__(self, **kwargs):

        # Map args from kwargs to instance-local variables
        for k, v in kwargs.items():
            if k in self.__attrs__:
                setattr(self, k, v)

        self._load()

    def _load(self):
        """Load each dotfile in the repository."""

        self.dotfiles = list()
        self._load_recursive()

    def _load_recursive(self, sub_dir=''):
        """Recursive helper for :meth:`_load`."""

        src_dir = os.path.join(self.repository, sub_dir)
        if sub_dir:
            # Add a dot to first level of packages
            dst_dir = os.path.join(self.homedir, '.%s' % sub_dir)
        else:
            dst_dir = os.path.join(self.homedir, sub_dir)

        all_repofiles = os.listdir(src_dir)
        repofiles_to_symlink = set(all_repofiles)

        for pat in self.ignore:
            repofiles_to_symlink.difference_update(
                    fnmatch.filter(all_repofiles, pat))

        for dotfile in repofiles_to_symlink:
            pkg_path = os.path.join(sub_dir, dotfile)
            if pkg_path in self.packages:
                self._load_recursive(pkg_path)
            else:
                self.dotfiles.append(Dotfile(dotfile[len(self.prefix):],
                    os.path.join(src_dir, dotfile), dst_dir,
                    add_dot=not bool(sub_dir), dry_run=self.dry_run))

        # Externals are top-level only
        if not sub_dir:
            for dotfile in self.externals.keys():
                self.dotfiles.append(Dotfile(dotfile,
                    os.path.expanduser(self.externals[dotfile]),
                    dst_dir, add_dot=not bool(sub_dir), dry_run=self.dry_run))

    def _fqpn(self, dotfile, pkg_name=None):
        """Return the fully qualified path to a dotfile."""
        if pkg_name is None:
            return os.path.join(self.repository,
                    self.prefix + os.path.basename(dotfile).strip('.'))
        return os.path.join(self.repository, self.prefix + pkg_name,
                os.path.basename(dotfile))

    def list(self, verbose=True):
        """List the contents of this repository."""

        for dotfile in sorted(self.dotfiles, key=lambda dotfile: dotfile.name):
            if dotfile.status or verbose:
                print(dotfile)

    def check(self):
        """List only unsynced and/or missing dotfiles."""

        self.list(verbose=False)

    def sync(self, files=None, force=False):

        """Synchronize this repository, creating and updating the necessary
        symbolic links."""

        # unless a set of files is specified, operate on all files
        if not files:
            dotfiles = self.dotfiles
        else:
            files = set(map(lambda x: os.path.join(self.homedir, x), files))
            dotfiles = [x for x in self.dotfiles if x.name in files]
            if not dotfiles:
                raise Exception("file not found")

        for dotfile in dotfiles:
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
            # See if file is inside a package
            file_dir, file_name = os.path.split(file)
            common_prefix = os.path.commonprefix([self.homedir, file_dir])
            sub_dir = file_dir[len(common_prefix) + 1:]
            pkg_name = sub_dir.lstrip('.')
            if pkg_name in self.packages:
                home = os.path.join(self.homedir, sub_dir)
                target = self._fqpn(file, pkg_name=pkg_name)
                dirname = os.path.dirname(target)
                if not os.path.exists(dirname):
                    os.makedirs(dirname)
            else:
                home = self.homedir
                target = self._fqpn(file)
            if sub_dir.startswith('.') or file_name.startswith('.'):
                dotfile = Dotfile(file, target, home, dry_run=self.dry_run)
                getattr(dotfile, action)()
            else:
                print("Skipping \"%s\", not a dotfile" % file)

    def move(self, target):
        """Move the repository to another location."""
        target = realpath_expanduser(target)

        if os.path.exists(target):
            raise ValueError('Target already exists: %s' % (target))

        if not self.dry_run:
            shutil.copytree(self.repository, target, symlinks=True)
            shutil.rmtree(self.repository)
        else:
            print("Recursive copy %s => %s" % (self.repository, target))
            print("Removing %s and everything under it" % self.repository)

        self.repository = target

        if not self.dry_run:
            self._load()
            self.sync(force=True)
