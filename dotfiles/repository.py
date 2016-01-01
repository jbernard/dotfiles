import py
from operator import attrgetter

from .dotfile import Dotfile


class Repository(object):
    """
    This class implements the 'repository' abstraction.

    A repository is a directory that contains dotfiles.  It has two primary
    attributes:

    repodir -- the location of the repository directory
    homedir -- the location of the home directory (primarily for testing)

    Both of the above attributes are received as string objects and converted
    to py.path.local objects for internal use.

    The repository implements these fundamental operations:

    status -- list the dotfiles (and their state) contained herein
    check  -- list any dotfiles unsynced or unmanaged that require attention
    sync   -- create some or all missing dotfile symlinks
    unsync -- remove some or all dotfile symlinks
    add    -- add a dotfile to this repository and create its symlink
    remove -- the opposited of add
    move   -- change the name of this repository and update dependent symlinks
    """

    def __init__(self, repodir, homedir='~'):
        self.repodir = repodir
        self.homedir = homedir

    def __str__(self):
        return self._contents() or '[no dotfiles found]'

    def __repr__(self):
        return '<Repository %r>' % self.repodir

    @property
    def repodir(self):
        return str(self._repodir)

    @repodir.setter
    def repodir(self, path):
        self._repodir = py.path.local(path, expanduser=True)

    @property
    def homedir(self):
        return str(self._homedir)

    @homedir.setter
    def homedir(self, path):
        self._homedir = py.path.local(path, expanduser=True)

    def _target_to_name(self, target):
        return py.path.local("%s/.%s" % (self.homedir, target.basename))

    def _load(self):
        """Given a repository path, discover all existing dotfiles."""
        dotfiles = []
        self._repodir.ensure(dir=1)
        targets = self._repodir.listdir()
        for target in targets:
            target = py.path.local(target)
            name = self._target_to_name(target)
            dotfiles.append(Dotfile(name, target))
        return sorted(dotfiles, key=attrgetter('name'))

    # TODO: pass dotfile objects to CLI instead of string

    def _contents(self, all=True):
        """Convert loaded contents to human readable form."""
        contents = ''
        dotfiles = self._load()
        for dotfile in dotfiles:
            if all or not dotfile.is_ok():
                contents += '\n%s' % dotfile
        return contents.lstrip()

    def status(self):
        """Returns a string list of all dotfiles."""
        return str(self)

    def check(self):
        """Returns a string list of only unsynced or missing dotfiles."""
        return self._contents(all=False)

    def sync(self):
        raise NotImplementedError

    def unsync(self):
        raise NotImplementedError

    def add(self):
        raise NotImplementedError

    def remove(self):
        raise NotImplementedError

    def move(self):
        raise NotImplementedError
