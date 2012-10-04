# -*- coding: utf-8 -*-

"""
dotfiles.core
~~~~~~~~~~~~~

This module provides the basic functionality of dotfiles.
"""

import os
import glob
import shutil
import fnmatch
import socket


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

    def _symlink(self):
        if 'relpath' in dir(os.path): # os.path.relpath() is new in Python 2.6
            os.symlink(os.path.relpath(self.target, os.path.dirname(self.name)),
                       self.name)
        else:
            os.symlink(self.target, self.name)

    def sync(self, force):
        if self.status == 'missing':
            self._symlink()
        elif self.status == 'unsynced':
            if not force:
                print("Skipping \"%s\", use --force to override"
                        % self.relpath)
                return
            if os.path.isdir(self.name) and not os.path.islink(self.name):
                shutil.rmtree(self.name)
            else:
                os.remove(self.name)
            self._symlink()

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
        self._symlink()

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

    def hosts_mode(self):
        return os.path.isdir(os.path.join(self.repository, 'all.host'))

    def host_dirname(self, hostname=None):
        if hostname is None and not self.hosts_mode():
            return self.repository
        else:
            if hostname is None:
                hostname = 'all'
            return os.path.join(self.repository, '%s.host' % hostname)

    def this_host_dotfiles(self, hostname=None):
        dotfiles = list(self.dotfiles['all']) # make a copy

        if self.hosts_mode():
            if hostname is None:
                hostname = socket.gethostname()
            try:
                dotfiles.extend(self.dotfiles[hostname])
            except KeyError:
                pass

        return dotfiles

    def _load(self):
        """Load each dotfile in the repository."""

        self.dotfiles = {}

        if self.hosts_mode():
            for hostdir in glob.glob("%s/*.host" % self.repository):
                if os.path.isdir(hostdir):
                    hostname = os.path.basename(hostdir).split('.')[0]
                    self.dotfiles[hostname] = self._load_host(hostname)
        else:
             self.dotfiles['all'] = self._load_host()

    def _load_host(self, hostname=None):
        """Load each dotfile for the supplied host."""

        directory = self.host_dirname(hostname)

        dotfiles = list()

        all_repofiles = list()
        for root, dirs, files in os.walk(directory):
            for f in files:
                f_rel_path = os.path.join(root, f)[len(directory)+1:]
                all_repofiles.append(f_rel_path)
            for d in dirs:
                if d[0] == '.':
                    dirs.remove(d)
                    continue
                dotdir = self._home_fqpn(os.path.join(root, d), hostname)
                if os.path.islink(dotdir):
                    dirs.remove(d)
                    d_rel_path = os.path.join(root, d)[len(directory)+1:]
                    all_repofiles.append(d_rel_path)
        repofiles_to_symlink = set(all_repofiles)

        for pat in self.ignore:
            repofiles_to_symlink.difference_update(
                    fnmatch.filter(all_repofiles, pat))

        for dotfile in repofiles_to_symlink:
            dotfiles.append(Dotfile(dotfile[len(self.prefix):],
                os.path.join(directory, dotfile), self.homedir))

        for dotfile in self.externals.keys():
            dotfiles.append(Dotfile(dotfile,
                os.path.expanduser(self.externals[dotfile]),
                self.homedir))

        return dotfiles

    def _repo_fqpn(self, homepath, hostname=None):
        """Return the fully qualified path to a dotfile in the repository."""

        dotfile_rel_path = homepath[len(self.homedir)+1:]
        dotfile_rel_repopath = self.prefix\
                               + dotfile_rel_path[1:] # remove leading '.'
        return os.path.join(self.host_dirname(hostname), dotfile_rel_repopath)

    def _home_fqpn(self, repopath, hostname=None):
        """Return the fully qualified path to a dotfile in the home dir."""

        dotfile_rel_path = repopath[len(self.host_dirname(hostname))+1+len(self.prefix):]
        return os.path.join(self.homedir, '.%s' % dotfile_rel_path)

    def list(self, verbose=True):
        """List the contents of this repository."""

        for dotfile in sorted(self.this_host_dotfiles(),
                              key=lambda dotfile: dotfile.name):
            if dotfile.status or verbose:
                print(dotfile)

    def check(self):
        """List only unsynced and/or missing dotfiles."""

        self.list(verbose=False)

    def sync(self, force=False, hostname=None):

        """Synchronize this repository, creating and updating the necessary
        symbolic links."""

        for dotfile in self.this_host_dotfiles(hostname):
            dotfile.sync(force)

    def add(self, files, hostname=None):
        """Add dotfile(s) to the repository."""

        self._perform_action('add', hostname, files)

    def remove(self, files, hostname=None):
        """Remove dotfile(s) from the repository."""

        self._perform_action('remove', hostname, files)

    def _perform_action(self, action, hostname, files):
        for file in files:
            file = file.rstrip('/')
            file = os.path.abspath(os.path.expanduser(file))
            if file[len(self.homedir)+1:].startswith('.'):
                getattr(Dotfile(file, self._repo_fqpn(file, hostname),
                                self.homedir),
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
