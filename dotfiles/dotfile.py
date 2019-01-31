import os

from click import echo
from hashlib import md5
from pathlib import Path

from .exceptions import \
    IsSymlink, NotASymlink, Exists, NotFound, Dangling, \
    TargetExists, TargetMissing

UNUSED = False


class Dotfile(object):
    """A configuration file managed within a repository.

    :param name:   name of the symlink in the home directory (~/.vimrc)
    :param target: where the symlink should point to (~/Dotfiles/vimrc)
    """
    RELATIVE_SYMLINKS = True

    def __init__(self, name, target):
        # if not name.is_file() and not name.is_symlink():
        #     raise NotFound(name)
        self.name = Path(name)
        self.target = Path(target)

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return '<Dotfile %r>' % self.name

    def _ensure_dirs(self, debug):
        """Ensure the directories for both name and target are in place.

        This is needed for the 'add' and 'link' operations where the
        directory structure is expected to exist.
        """
        def ensure(dir, debug):
            if not dir.is_dir():
                if debug:
                    echo('MKDIR  %s' % dir)
                else:
                    dir.mkdir(parents=True)

        ensure(self.name.parent, debug)
        ensure(self.target.parent, debug)

    def _prune_dirs(self, debug):
        # TODO
        if debug:
            echo('PRUNE  <TODO>')

    def _link(self, debug, home):
        """Create a symlink from name to target, no error checking."""
        source = self.name
        target = self.target

        if self.name.is_symlink():
            source = self.target
            target = self.name.resolve()
        elif self.RELATIVE_SYMLINKS:
            target = os.path.relpath(target, source.parent)

        if debug:
            echo('LINK   %s -> %s' % (source, target))
        else:
            source.symlink_to(target)

    def _unlink(self, debug):
        """Remove a symlink in the home directory, no error checking."""
        if debug:
            echo('UNLINK %s' % self.name)
        else:
            self.name.unlink()

    def short_name(self, home):
        """A shorter, more readable name given a home directory."""
        return self.name.relative_to(home)

    def _is_present(self):
        """Is this dotfile present in the repository?"""
        return self.name.is_symlink() and (self.name.resolve() == self.target)

    def _same_contents(self):
        return (md5(self.name.read_bytes()).hexdigest() == \
                md5(self.target.read_bytes()).hexdigest())

    @property
    def state(self):
        """The current state of this dotfile."""
        if self.target.is_symlink():
            return 'external'

        if not self.name.exists():
            # no $HOME file or symlink
            return 'missing'

        if self.name.is_symlink():
            # name exists, is a link, but isn't a link to the target
            if not self.name.samefile(self.target):
                return 'conflict'
            return 'link'

        if not self._same_contents():
            # name exists, is a file, but differs from the target
            return 'conflict'

        return 'copy'

    def add(self, copy=False, debug=False, home=Path.home()):
        """Move a dotfile to its target and create a link.

        The link is either a symlink or a copy.
        """
        if copy:
            raise NotImplementedError()
        if self._is_present():
            raise IsSymlink(self.name)
        if self.target.exists():
            raise TargetExists(self.name)
        self._ensure_dirs(debug)
        if not self.name.is_symlink():
            if debug:
                echo('MOVE   %s -> %s' % (self.name, self.target))
            else:
                self.name.replace(self.target)
        self._link(debug, home)

    def remove(self, copy=UNUSED, debug=False):
        """Remove a dotfile and move target to its original location."""
        if not self.name.is_symlink():
            raise NotASymlink(self.name)
        if not self.target.is_file():
            raise TargetMissing(self.name)
        self._unlink(debug)
        if debug:
            echo('MOVE   %s -> %s' % (self.target, self.name))
        else:
            self.target.replace(self.name)

    def enable(self, copy=False, debug=False, home=Path.home()):
        """Create a symlink or copy from name to target."""
        if copy:
            raise NotImplementedError()
        if self.name.exists():
            raise Exists(self.name)
        if not self.target.exists():
            raise TargetMissing(self.name)
        self._ensure_dirs(debug)
        self._link(debug, home)

    def disable(self, copy=UNUSED, debug=False):
        """Remove a dotfile from name to target."""
        if not self.name.is_symlink():
            raise NotASymlink(self.name)
        if self.name.exists():
            if not self.target.exists():
                raise TargetMissing(self.name)
            if not self.name.samefile(self.target):
                raise RuntimeError
        self._unlink(debug)
        self._prune_dirs(debug)
