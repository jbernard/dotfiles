import py
from click import echo

from .dotfile import Dotfile
from .exceptions import DotfileException, TargetIgnored, IsDirectory, \
    InRepository


class Repository(object):
    """A repository is a directory that contains dotfiles.

    :param repodir: the location of the repository directory
    :param homedir: the location of the home directory (primarily for testing)
    :param ignore:  a list of targets to ignore
    """

    def __init__(self, repodir, homedir, ignore=[]):
        self.ignore = ignore
        self.homedir = homedir

        # create repository if needed
        self.repodir = repodir.ensure(dir=1)

    def __str__(self):
        """Return human-readable repository contents."""
        return ''.join('%s\n' % item for item in self.contents()).rstrip()

    def __repr__(self):
        return '<Repository %r>' % self.repodir

    def _target_to_name(self, target):
        """Return the expected symlink for the given repository target."""
        return self.homedir.join(self.repodir.bestrelpath(target))

    def _name_to_target(self, name):
        """Return the expected repository target for the given symlink."""
        return self.repodir.join(self.homedir.bestrelpath(name))

    def dotfile(self, name):
        """Return a valid dotfile for the given path."""

        # XXX: it must be below the home directory
        #      it cannot be contained in the repository
        #      it cannot be ignored
        #      it must be a file

        target = self._name_to_target(name)
        if target.basename in self.ignore:
            raise TargetIgnored(name)
        if name.check(dir=1):
            raise IsDirectory(name)

        for path in name.parts():
            try:
                if self.repodir.samefile(path):
                    raise InRepository(name)
            except py.error.ENOENT:
                # this occurs when the symlink does not yet exist
                continue

        # if not self.homedir.samefile(name.dirname):
        #     raise NotRootedInHome(name)
        # if name.dirname != self.homedir:
        #     raise IsNested(name)
        # if name.basename[0] != '.':
        #     raise NotADotfile(name)

        return Dotfile(name, target)

    def dotfiles(self, paths):
        """Return a list of dotfiles given a path."""

        paths = map(py.path.local, paths)

        rv = []
        for path in paths:
            try:
                rv.append(self.dotfile(path))
            except DotfileException as err:
                echo(err)

        return rv

    def contents(self):
        """Return a list of all dotfiles in the repository path."""
        def filter(node):
            return node.check(dir=0) and node.basename not in self.ignore

        def recurse(node):
            return node.basename not in self.ignore

        def construct(target):
            return Dotfile(self._target_to_name(target), target)

        return map(construct, self.repodir.visit(filter, recurse, sort=True))
