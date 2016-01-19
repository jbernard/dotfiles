import py
from click import echo

from .exceptions import IsSymlink, NotASymlink
from .exceptions import TargetExists, TargetMissing
from .exceptions import Exists


class Dotfile(object):
    """An configuration file managed within a repository.

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
        def ensure(dir, debug):
            if not dir.check():
                if debug:
                    echo('MKDIR  %s' % dir)
                else:
                    dir.ensure_dir()
        ensure(py.path.local(self.name.dirname), debug)
        ensure(py.path.local(self.target.dirname), debug)

    def _link(self, debug):
        if debug:
            echo('LINK   %s -> %s' % (self.name, self.target))
        else:
            self.name.mksymlinkto(self.target, absolute=0)

    def _unlink(self, debug):
        if debug:
            echo('UNLINK %s' % self.name)
        else:
            self.name.remove()

    def short_name(self, homedir):
        return homedir.bestrelpath(self.name)

    @property
    def state(self):
        if self.target.check(exists=0):
            # only for testing, cli should never reach this state
            return 'error'
        elif self.name.check(exists=0):
            # no $HOME symlink
            return 'missing'
        elif self.name.check(link=0) or not self.name.samefile(self.target):
            # if name exists but isn't a link to the target
            return 'conflict'
        return 'ok'

    def add(self, debug=False):
        if self.name.check(link=1):
            raise IsSymlink(self.name)
        if self.target.check(exists=1):
            raise TargetExists(self.name)
        self._ensure_dirs(debug)
        if debug:
            echo('MOVE   %s -> %s' % (self.name, self.target))
        else:
            self.name.move(self.target)
        self._link(debug)

    def remove(self, debug=False):
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
        if self.name.check(exists=1):
            raise Exists(self.name)
        if self.target.check(exists=0):
            raise TargetMissing(self.name)
        self._ensure_dirs(debug)
        self._link(debug)

    def unlink(self, debug=False):
        if self.name.check(link=0):
            raise NotASymlink(self.name)
        if self.target.check(exists=0):
            raise TargetMissing(self.name)
        if not self.name.samefile(self.target):
            raise RuntimeError
        self._unlink(debug)
