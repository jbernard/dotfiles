import errno


class Dotfile(object):
    """
    This class implements the 'dotfile' abstraction.

    A dotfile has two primary attributes:

    name -- name of dotfile in the home directory (~/.vimrc)
    target -- target the dotfile should point to (~/Dotfiles/vimrc)

    The above attributes are both py.path.local objects.

    The goal is for there to be no special logic or stored global state.  Only
    the implementation of three operations made available to the caller:

    add -- moves a dotfile into the repository and replaces it with a symlink
    remove -- the opposite of add
    sync -- ensure that each repository file has a corresponding symlink

    This is where most filesystem operations (link, delete, etc) should be
    called, and not in the layers above.
    """

    states = {
        'error':    {'text': '(error)',    'color': 'red'},
        'missing':  {'text': '(missing)',  'color': 'yellow'},
        'conflict': {'text': '(conflict)', 'color': 'yellow'},
        'ok':       {'text': '(ok)',       'color': 'green'},
    }

    def __init__(self, name, target):
        self.name = name
        self.target = target
        self._set_state()

    def __str__(self):
        short_name, _ = self._truncate_paths()
        return '%-18s %-s' % (short_name, self.state['text'])

    def __repr__(self):
        return '<Dotfile %r>' % self.name

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

    def is_ok(self):
        return self.state == self.states['ok']

    def _set_state(self):

        # only for testing, cli should never reach this state
        if self.target.check(exists=0):
            self.state = self.states['error']

        # no $HOME symlink
        elif self.name.check(exists=0):
            self.state = self.states['missing']

        # if name exists but isn't a link to the target
        elif self.name.check(link=0) or not self.name.samefile(self.target):
            self.state = self.states['conflict']

        # all good
        else:
            self.state = self.states['ok']

    def _truncate_paths(self):
        discard = len(str(self.name.common(self.target))) + 1
        return (str(self.name)[discard:], str(self.target)[discard:])
