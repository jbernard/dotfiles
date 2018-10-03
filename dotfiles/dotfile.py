from click import echo
from pathlib import Path

from .exceptions import \
    IsSymlink, NotASymlink, TargetExists, TargetMissing, Exists


class Dotfile(object):
    """A configuration file managed within a repository.

    :param name:   name of the symlink in the home directory (~/.vimrc)
    :param target: where the symlink should point to (~/Dotfiles/vimrc)
    """

    def __init__(self, name, target):
        self.name = name
        self.target = target

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
            if not dir.check():
                if debug:
                    echo('MKDIR  %s' % dir)
                else:
                    dir.ensure_dir()

        ensure(py.path.local(self.name.dirname), debug)
        ensure(py.path.local(self.target.dirname), debug)

    def _link(self, debug):
        """Create a symlink from name to target, no error checking."""
        source = self.name
        target = self.target
        if self.name.islink():
            source = self.target
            target = self.name.realpath()
        if debug:
            echo('LINK   %s -> %s' % (source, target))
        else:
            source.mksymlinkto(target, absolute=0)

    def _unlink(self, debug):
        """Remove a symlink in the home directory, no error checking."""
        if debug:
            echo('UNLINK %s' % self.name)
        else:
            self.name.remove()

    def short_name(self, homedir):
        """A shorter, more readable name given a home directory."""
        return self.name.relative_to(homedir)
        # return homedir.bestrelpath(self.name)

    def is_present(self):
        """Is this dotfile present in the repository?"""
        return self.name.islink() and (self.name.realpath() == self.target)

    @property
    def state(self):
        """The current state of this dotfile."""
        if self.target.check(exists=0):
            # only for testing, cli should never reach this state
            return 'error'
        elif self.name.check(exists=0):
            # no $HOME file or symlink
            return 'missing'
        elif self.name.islink():
            # name exists, is a link, but isn't a link to the target
            if not self.name.samefile(self.target):
                return 'conflict'
        else:
            # name exists, is a file, but differs from the target
            if self.name.computehash() != self.target.computehash():
                return 'conflict'
        return 'ok'

    def add(self, debug=False):
        """Move a dotfile to it's target and create a symlink."""
        if self.is_present():
            raise IsSymlink(self.name)
        if self.target.check(exists=1):
            raise TargetExists(self.name)
        self._ensure_dirs(debug)
        if not self.name.islink():
            if debug:
                echo('MOVE   %s -> %s' % (self.name, self.target))
            else:
                self.name.move(self.target)
        self._link(debug)

    def remove(self, debug=False):
        """Remove a symlink and move the target back to its name."""
        if self.name.check(link=0):
            raise NotASymlink(self.name)
        if self.target.check(exists=0):
            raise TargetMissing(self.name)
        self._unlink(debug)
        if debug:
            echo('MOVE   %s -> %s' % (self.target, self.name))
        else:
            self.target.move(self.name)

    def link(self, debug=False):
        """Create a symlink from name to target."""
        if self.name.check(exists=1):
            raise Exists(self.name)
        if self.target.check(exists=0):
            raise TargetMissing(self.name)
        self._ensure_dirs(debug)
        self._link(debug)

    def unlink(self, debug=False):
        """Remove a symlink from name to target."""
        if self.name.check(link=0):
            raise NotASymlink(self.name)
        if self.target.check(exists=0):
            raise TargetMissing(self.name)
        if not self.name.samefile(self.target):
            raise RuntimeError
        self._unlink(debug)
