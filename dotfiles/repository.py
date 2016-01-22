import click
import py.path
from operator import attrgetter

from .dotfile import Dotfile
from .exceptions import DotfileException, TargetIgnored
from .exceptions import NotRootedInHome, InRepository, IsDirectory


class Repository(object):
    """A repository is a directory that contains dotfiles.

    :param path: the location of the repository directory
    :param ignore_patterns: a list of glob patterns to ignore
    :param preserve_leading_dot: whether to preserve the target's leading dot
    :param home_directory: the location of the home directory
    """

    home_directory = py.path.local('~/', expanduser=True)

    def __init__(self, path,
                 ignore_patterns=[],
                 preserve_leading_dot=False,
                 home_directory=home_directory):

        # create repository directory if not found
        self.path = py.path.local(path).ensure_dir()

        self.home_directory = home_directory
        self.ignore_patterns = ignore_patterns
        self.preserve_leading_dot = preserve_leading_dot

    def __str__(self):
        """Return human-readable repository contents."""
        return ''.join('%s\n' % item for item in self.contents()).rstrip()

    def __repr__(self):
        return '<Repository %r>' % self.path

    def _ignore(self, path):
        for pattern in self.ignore_patterns:
            if path.fnmatch(pattern):
                return True
        return False

    def _dotfile_path(self, target):
        """Return the expected symlink for the given repository target."""
        relpath = self.path.bestrelpath(target)
        if self.preserve_leading_dot:
            return self.home_directory.join(relpath)
        else:
            return self.home_directory.join('.%s' % relpath)

    def _dotfile_target(self, path):
        """Return the expected repository target for the given symlink."""
        relpath = self.home_directory.bestrelpath(path)
        if self.preserve_leading_dot:
            return self.path.join(relpath)
        else:
            return self.path.join(relpath[1:])

    def _dotfile(self, path):
        """Return a valid dotfile for the given path."""
        target = self._dotfile_target(path)

        if not path.fnmatch('%s/*' % self.home_directory):
            raise NotRootedInHome(path)
        if path.fnmatch('%s/*' % self.path):
            raise InRepository(path)
        if self._ignore(target):
            raise TargetIgnored(path)
        if path.check(dir=1):
            raise IsDirectory(path)

        return Dotfile(path, target)

    def _contents(self, dir):
        """Return all unignored files contained below a directory."""
        def filter(node):
            return node.check(dir=0) and not self._ignore(node)

        return dir.visit(filter, lambda x: not self._ignore(x))

    def contents(self):
        """Return a list of dotfiles for each file in the repository."""
        def construct(target):
            return Dotfile(self._dotfile_path(target), target)

        contents = self._contents(self.path)
        return sorted(map(construct, contents), key=attrgetter('path'))

    def dotfiles(self, paths):
        """Return a collection of dotfiles given a list of paths.

        This function takes a list of paths where each path can be a file or a
        directory.  Each directory is recursively expaned into file paths.
        Once the list is converted into only files, dotifles are constructed
        for each path in the set.  This set of dotfiles is returned to the
        caller.
        """
        paths = list(set(map(py.path.local, paths)))

        for path in paths:
            if path.check(dir=1):
                paths.extend(self._contents(path))
                paths.remove(path)

        def construct(path):
            try:
                return self._dotfile(path)
            except DotfileException as err:
                click.echo(err)
                return None

        return [d for d in map(construct, paths) if d is not None]

    def prune(self):
        """Remove any empty directories in the repository.

        After a remove operation, there may be empty directories remaining.
        The Dotfile class has no knowledge of other dotfiles in the repository,
        so pruning must take place explicitly after such operations occur.
        """
        def filter(node):
            return node.check(dir=1) and not self._ignore(node)

        for dir in self.path.visit(filter, lambda x: not self._ignore(x)):
            if not len(dir.listdir()):
                dir.remove()
