import os

from click import echo
from pathlib import Path
from fnmatch import fnmatch
from operator import attrgetter

from .dotfile import Dotfile
from .exceptions import DotfileException, TargetIgnored
from .exceptions import NotRootedInHome, InRepository, IsDirectory


class Repositories(object):
    """An iterable collection of repository objects."""
    def __init__(self, paths, home=Path.home()):
        self.repos = []
        for path in paths:
            self.repos.append(Repository(path, home))

    def __len__(self):
        return len(self.repos)

    def __getitem__(self, index):
        return self.repos[index]


class Repository(object):
    """A repository is a directory that contains dotfiles."""
    REMOVE_LEADING_DOT = True
    IGNORE_PATTERNS = ['.git/*', '.gitignore', 'README*', '*~']

    def __init__(self, path, home=Path.home()):
        self.path = Path(path).expanduser().resolve()
        self.home = Path(home).expanduser().resolve()

        if not self.path.exists():
            echo('Creating new repository: %s' % self.path)
            self.path.mkdir(parents=True, exist_ok=True)

        if not self.home.exists():
            raise FileNotFoundError(self.home)


    def __str__(self):
        """Return human-readable repository contents."""
        return ''.join('%s\n' % x for x in self.contents()).rstrip()

    def __repr__(self):
        return '<Repository %r>' % str(self.path)

    def _ignore(self, path):
        """Test whether a dotfile should be ignored."""
        for pattern in self.IGNORE_PATTERNS:
            if fnmatch(str(path), '*/%s' % pattern):
                return True
        return False

    def _dotfile_path(self, target):
        """Return the expected symlink for the given repository target."""
        relpath = target.relative_to(self.path)
        if self.REMOVE_LEADING_DOT:
            return self.home / ('.%s' % relpath)
        else:
            return self.home / relpath

    def _dotfile_target(self, path):
        """Return the expected repository target for the given symlink."""
        try:
            # is the dotfile within the home directory?
            relpath = str(path.relative_to(self.home))
        except ValueError:
            raise NotRootedInHome(path)

        if self.REMOVE_LEADING_DOT and relpath[0] == '.':
            relpath = relpath[1:]

        return self.path / relpath

    def _dotfile(self, path):
        """Return a valid dotfile for the given path."""
        target = self._dotfile_target(path)

        if not fnmatch(str(path), '%s/*' % self.home):
            raise NotRootedInHome(path)
        if fnmatch(str(path), '%s/*' % self.path):
            raise InRepository(path)
        if self._ignore(target):
            raise TargetIgnored(path)
        if path.is_dir():
            raise IsDirectory(path)

        return Dotfile(path, target)

    def _contents(self, dir):
        """Return all unignored files contained below a directory."""
        def skip(path):
            return path.is_dir() or self._ignore(path)

        return [x for x in dir.rglob('*') if not skip(x)]

    def contents(self):
        """Return dotfile objects for each file in the repository."""
        def construct(target):
            return Dotfile(self._dotfile_path(target), target)

        contents = self._contents(self.path)
        return sorted(map(construct, contents), key=attrgetter('name'))

    def dotfiles(self, paths):
        """Return a collection of dotfiles given a list of paths.

        This function takes a list of paths where each path can be a
        file or a directory.  Each directory is recursively expaned into
        file paths.  Once the list is converted into only files, Dotfile
        objects are constructed for each item in the set.  This set of
        dotfiles is returned to the caller.
        """
        paths = [Path(x).expanduser().absolute() for x in paths]

        for path in paths:
            if path.is_dir():
                paths.extend(self._contents(path))
                paths.remove(path)

        def construct(path):
            try:
                return self._dotfile(path)
            except DotfileException as err:
                echo(err)
                return None

        return [d for d in map(construct, paths) if d is not None]

    def prune(self, debug=False):
        """Remove any empty directories in the repository.

        After a remove operation, there may be empty directories remaining.
        The Dotfile class has no knowledge of other dotfiles in the repository,
        so pruning must take place explicitly after such operations occur.
        """
        def skip(path):
            return self._ignore(path) or path == str(self.path)

        # TODO: this *could* use pathlib instead

        dirs = reversed([dir for dir, subdirs, files in
                         os.walk(str(self.path)) if not skip(dir)])

        for dir in dirs:
            if not len(os.listdir(dir)):
                if debug:
                    echo('PRUNE  %s' % (dir))
                os.rmdir(dir)
