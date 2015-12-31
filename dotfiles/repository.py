import py
from .dotfile import Dotfile
from operator import attrgetter


class Repository(object):
    """
    This class implements the 'repository' abstraction.

    A repository is a directory that contains dotfiles.

    TODO
    """

    def __init__(self, path, homedir):
        self.path = path
        self.homedir = homedir
        self.dotfiles = self._discover()

    def _target_to_name(self, target):
        return py.path.local("{}/.{}".format(self.homedir, target.basename))

    def _discover(self):
        """Given a repository path, discover all existing dotfiles."""
        dotfiles = []
        for target in self.path.listdir():
            target = py.path.local(target)
            name = self._target_to_name(target)
            dotfiles.append(Dotfile(name, target))
        return sorted(dotfiles, key=attrgetter('name'))

    def _list(self, all=True):
        listing = ''
        for dotfile in self.dotfiles:
            if all or dotfile.invalid():
                listing += '\n{}'.format(dotfile)
        return listing.lstrip()

    def __str__(self):
        """Returns a string list the all dotfiles in this repository."""
        return self._list()

    def check(self):
        """Returns a string of only unsynced or missing dotfiles."""
        return self._list(all=False)

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
