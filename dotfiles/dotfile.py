import errno


def unique_suffix(path_a, path_b):
    discard = len(str(path_a.common(path_b))) + 1
    return (str(path_a)[discard:], str(path_b)[discard:])


class Dotfile(object):
    """
    This class implements the 'dotfile' abstraction.

    A dotfile has two primary attributes:

    name -- name of symlink in the home directory (~/.vimrc)
    target -- where the symlink should point to (~/Dotfiles/vimrc)

    The above attributes are both py.path.local objects.

    The goal is for there to be no special logic or stored global state.  Only
    the implementation of three operations made available to the caller:

    add    -- move a dotfile into the repository and replace it with a symlink
    remove -- the opposite of add
    sync   -- ensure that each repository file has a corresponding symlink
    unsync -- remove the symlink leaving only the repository file

    This is where most filesystem operations (link, delete, etc) should be
    called, and not in the layers above.
    """

    def __init__(self, name, target):
        self.name = name
        self.target = target

    def __str__(self):
        short_name, _ = unique_suffix(self.name, self.target)
        return '%s' % short_name

    def __repr__(self):
        return '<Dotfile %r>' % self.name

    @property
    def state(self):

        # lets be optimistic
        state = 'ok'

        if self.target.check(exists=0):
            # only for testing, cli should never reach this state
            state = 'error'
        elif self.name.check(exists=0):
            # no $HOME symlink
            state = 'missing'
        elif self.name.check(link=0) or not self.name.samefile(self.target):
            # if name exists but isn't a link to the target
            state = 'conflict'

        return state

    def add(self):
        if self.target.check(exists=1):
            raise OSError(errno.EEXIST, self.target)
        self.name.move(self.target)
        self.sync()

    def remove(self):
        if self.target.check(exists=0):
            raise OSError(errno.ENOENT, self.target)
        self.name.remove()
        self.target.move(self.name)

    def sync(self):
        self.name.mksymlinkto(self.target)

    def unsync(self):
        self.name.remove()
