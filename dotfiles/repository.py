from click import echo
from pathlib import Path
from operator import attrgetter

from .dotfile import Dotfile
from .exceptions import DotfileException, TargetIgnored
from .exceptions import NotRootedInHome, InRepository, IsDirectory

PATH = '~/Dotfiles'
HOMEDIR = Path.home()
REMOVE_LEADING_DOT = True
IGNORE_PATTERNS = ['.git', '.gitignore', 'README*', '*~']


class Repositories(object):
    """An iterable collection of repository objects."""

    def __init__(self, paths, dot):
        if not paths:
            paths = [PATH]
        if dot is None:
            dot = REMOVE_LEADING_DOT

        self.repos = []
        for path in paths:
            path = Path(path).expanduser()
            self.repos.append(Repository(path, dot))

    def __len__(self):
        return len(self.repos)

    def __getitem__(self, index):
        return self.repos[index]


class Repository(object):
    """A repository is a directory that contains dotfiles.

    :param path: the location of the repository directory
    :param homedir: the location of the home directory
    :param remove_leading_dot: whether to remove the target's leading dot
    :param ignore_patterns: a list of glob patterns to ignore
    """

    def __init__(self, path,
                 homedir=HOMEDIR,
                 remove_leading_dot=REMOVE_LEADING_DOT,
                 ignore_patterns=IGNORE_PATTERNS):
        self.path = Path(path)
        self.homedir = Path(homedir)
        self.remove_leading_dot = remove_leading_dot
        self.ignore_patterns = ignore_patterns

        # create repository directory if missing
        self.path.mkdir(parents=True, exist_ok=True)

    def __str__(self):
        """Return human-readable repository contents."""
        return ''.join('%s\n' % x for x in self.contents()).rstrip()

    def __repr__(self):
        return '<Repository %r>' % str(self.path)

    def _ignore(self, path):
        if not path.is_file():
            return True
        for pattern in self.ignore_patterns:
            if path.match(pattern):
                return True
        return False

    def _dotfile_path(self, target):
        """Return the expected symlink for the given repository target."""

        relpath = target.relative_to(self.path)
        if self.remove_leading_dot:
            return self.homedir / ('.%s' % relpath)
        else:
            return self.homedir / relpath

    def _dotfile_target(self, path):
        """Return the expected repository target for the given symlink."""

        relpath = str(path.relative_to(self.homedir))
        if self.remove_leading_dot:
            return self.path / relpath[1:]
        else:
            return self.path / relpath

    def _dotfile(self, path):
        """Return a valid dotfile for the given path."""

        target = self._dotfile_target(path)

        if not path.fnmatch('%s/*' % self.homedir):
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
        return [x for x in dir.rglob('*') if not self._ignore(x)]

    def contents(self):
        """Return a list of dotfiles for each file in the repository."""

        def construct(target):
            return Dotfile(self._dotfile_path(target), target)

        contents = self._contents(self.path)
        return sorted(map(construct, contents), key=attrgetter('name'))

    def dotfiles(self, paths):
        """Return a collection of dotfiles given a list of paths.

        This function takes a list of paths where each path can be a file or a
        directory.  Each directory is recursively expaned into file paths.
        Once the list is converted into only files, dotifles are constructed
        for each path in the set.  This set of dotfiles is returned to the
        caller.
        """

        paths = list(set(map(Path, paths)))

        for path in paths:
            if path.check(dir=1):
                paths.extend(self._contents(path))
                paths.remove(path)

        def construct(path):
            try:
                return self._dotfile(path)
            except DotfileException as err:
                echo(err)
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
