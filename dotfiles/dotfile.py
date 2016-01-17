import py
from click import echo
from errno import EEXIST, ENOENT

from .exceptions import IsDirectory, IsSymlink, NotASymlink, DoesNotExist, \
    TargetExists, TargetMissing


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

    def _ensure_subdirs(self, debug):
        target_dir = py.path.local(self.target.dirname)
        if not target_dir.check():
            if debug:
                echo('MKDIR  %s' % self.target.dirname)
            else:
                target_dir.ensure_dir()

    def _remove_subdirs(self, debug):
        # TODO
        pass

    def _add(self, debug):
        self._ensure_subdirs(debug)
        if debug:
            echo('MOVE   %s -> %s' % (self.name, self.target))
        else:
            self.name.move(self.target)
        self._link(debug)

    def _remove(self, debug):
        self._unlink(debug)
        if debug:
            echo('MOVE   %s -> %s' % (self.target, self.name))
        else:
            self.target.move(self.name)
        self._remove_subdirs(debug)

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
        if self.name.check(file=0):
            raise DoesNotExist(self.name)
        if self.name.check(dir=1):
            raise IsDirectory(self.name)
        if self.name.check(link=1):
            raise IsSymlink(self.name)
        if self.target.check(exists=1):
            raise TargetExists(self.name)
        self._add(debug)

    def remove(self, debug=False):
        if not self.name.check(link=1):
            raise NotASymlink(self.name)
        if self.target.check(exists=0):
            raise TargetMissing(self.name)
        self._remove(debug)

    # TODO: replace exceptions

    def link(self, debug=False):
        if self.name.check(exists=1):
            raise OSError(EEXIST, self.name)
        if self.target.check(exists=0):
            raise OSError(ENOENT, self.target)
        self._link(debug)

    def unlink(self, debug=False):
        if self.name.check(link=0):
            raise Exception('%s is not a symlink' % self.name.basename)
        if self.target.check(exists=0):
            raise Exception('%s does not exist' % self.target)
        if not self.name.samefile(self.target):
            raise Exception('good lord')
        self._unlink(debug)
