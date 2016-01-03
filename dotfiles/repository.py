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
    """

    def __init__(self, repodir, homedir='~'):
        self.repodir = repodir
        self.homedir = homedir

    def __str__(self):
        """Convert repository contents to human readable form."""
        return ''.join('%s\n' % item for item in self.contents()).rstrip()

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

    def _expected_name(self, target):
        return py.path.local("%s/.%s" % (self.homedir, target.basename))

    def contents(self):
        """Given a repository path, discover all existing dotfiles."""
        contents = []
        self._repodir.ensure(dir=1)
        for target in self._repodir.listdir():
            target = py.path.local(target)
            contents.append(Dotfile(self._expected_name(target), target))
        return sorted(contents, key=attrgetter('name'))

    def rename(self):
        raise NotImplementedError
