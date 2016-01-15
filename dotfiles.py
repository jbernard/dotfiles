import py
import os
import click
import errno
from operator import attrgetter


DEFAULT_HOMEDIR = os.path.expanduser('~/')
DEFAULT_REPO_PATH = os.path.expanduser('~/Dotfiles')
DEFAULT_REPO_IGNORE = ['.git', '.gitignore']


class DotfileException(Exception):
    """An exception the CLI can handle and show to the user."""

    def __init__(self, path, message='an unknown error occurred'):
        self.message = '\'%s\' %s' % (path, message)
        Exception.__init__(self, self.message)

    def __str__(self):
        return 'ERROR: %s' % self.message


class TargetIgnored(DotfileException):

    def __init__(self, path):
        DotfileException.__init__(self, path, 'targets an ignored file')


class IsDirectory(DotfileException):

    def __init__(self, path):
        DotfileException.__init__(self, path, 'is a directory')


class IsSymlink(DotfileException):

    def __init__(self, path):
        DotfileException.__init__(self, path, 'is a symlink')


class NotASymlink(DotfileException):

    def __init__(self, path):
        DotfileException.__init__(self, path, 'is not a symlink')


class InRepository(DotfileException):

    def __init__(self, path):
        DotfileException.__init__(self, path, 'is within the repository')


class NotRootedInHome(DotfileException):

    def __init__(self, path):
        DotfileException.__init__(self, path, 'not rooted in home directory')


class IsNested(DotfileException):

    def __init__(self, path):
        DotfileException.__init__(self, path, 'is nested')


class NotADotfile(DotfileException):

    def __init__(self, path):
        DotfileException.__init__(self, path, 'is not a dotfile')


class DoesNotExist(DotfileException):

    def __init__(self, path):
        DotfileException.__init__(self, path, 'doest not exist')


class TargetExists(DotfileException):

    def __init__(self, path):
        DotfileException.__init__(self, path, 'target already exists')


class TargetMissing(DotfileException):

    def __init__(self, path):
        DotfileException.__init__(self, path, 'target is missing')


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
        return self.homedir.join('.%s' % target.basename)

    def _name_to_target(self, name):
        """Return the expected repository target for the given symlink."""
        return self.repodir.join(self.homedir.bestrelpath(name)[1:])

    def dotfile(self, name):
        """Return a valid dotfile for the given path."""

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
        if name.basename[0] != '.':
            raise NotADotfile(name)

        return Dotfile(name, target)

    def dotfiles(self, path):
        """Return a list of dotfiles given a path."""

        if path.check(dir=1):
            raise IsDirectory(path)

        return self.dotfile(path)

    def contents(self):
        """Return a list of all dotfiles in the repository path."""
        contents = []
        for target in self.repodir.listdir():
            target = py.path.local(target)
            if target.basename not in self.ignore:
                contents.append(Dotfile(self._target_to_name(target), target))
        return sorted(contents, key=attrgetter('name'))


class Dotfile(object):
    """An configuration file managed within a repository.

    :param name:   name of the symlink in the home directory (~/.vimrc)
    :param target: where the symlink should point to (~/Dotfiles/vimrc)
    """

    def __init__(self, name, target):
        self.name = name
        self.target = target

    def __str__(self):
        return self.name.basename

    def __repr__(self):
        return '<Dotfile %r>' % self.name

    def _ensure_target_dir(self, verbose):
        target_dir = py.path.local(self.target.dirname)
        if not target_dir.check():
            if verbose:
                click.echo('MKDIR  %s' % self.target.dirname)
            target_dir.ensure(dir=1)

    def _add(self, verbose):
        self._ensure_target_dir(verbose)
        if verbose:
            click.echo('MOVE   %s -> %s' % (self.name, self.target))
        self.name.move(self.target)
        self._link(verbose)

    def _remove(self, verbose):
        self._unlink(verbose)
        if verbose:
            click.echo('MOVE   %s -> %s' % (self.target, self.name))
        self.target.move(self.name)
        # TODO: remove directory if empty

    def _link(self, verbose):
        if verbose:
            click.echo('LINK   %s -> %s' % (self.name, self.target))
        self.name.mksymlinkto(self.target, absolute=0)

    def _unlink(self, verbose):
        if verbose:
            click.echo('UNLINK %s' % self.name)
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

    def add(self, verbose=False):
        if self.name.check(file=0):
            raise DoesNotExist(self.name)
        if self.name.check(dir=1):
            raise IsDirectory(self.name)
        if self.name.check(link=1):
            raise IsSymlink(self.name)
        if self.target.check(exists=1):
            raise TargetExists(self.name)
        self._add(verbose)

    def remove(self, verbose=False):
        if not self.name.check(link=1):
            raise NotASymlink(self.name)
        if self.target.check(exists=0):
            raise TargetMissing(self.name)
        self._remove(verbose)

    # TODO: replace exceptions

    def link(self, verbose=False):
        if self.name.check(exists=1):
            raise OSError(errno.EEXIST, self.name)
        if self.target.check(exists=0):
            raise OSError(errno.ENOENT, self.target)
        self._link(verbose)

    def unlink(self, verbose=False):
        if self.name.check(link=0):
            raise Exception('%s is not a symlink' % self.name.basename)
        if self.target.check(exists=0):
            raise Exception('%s does not exist' % self.target)
        if not self.name.samefile(self.target):
            raise Exception('good lord')
        self._unlink(verbose)


pass_repo = click.make_pass_decorator(Repository)


@click.group(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('--repository', type=click.Path(), show_default=True,
              default=DEFAULT_REPO_PATH)
@click.version_option()
@click.pass_context
def cli(ctx, repository):
    """Dotfiles is a tool to make managing your dotfile symlinks in $HOME easy,
    allowing you to keep all your dotfiles in a single directory.
    """
    ctx.obj = Repository(py.path.local(repository),
                         py.path.local(DEFAULT_HOMEDIR),
                         DEFAULT_REPO_IGNORE)


@cli.command()
@click.option('-v', '--verbose', is_flag=True, help='Show executed commands.')
@click.argument('files', nargs=-1, type=click.Path(exists=True))
@pass_repo
def add(repo, verbose, files):
    """Replace file with symlink."""
    # TODO: repo.dotfiles() for directories
    for filename in files:
        try:
            repo.dotfile(py.path.local(filename)).add(verbose)
            click.echo('added \'%s\'' % filename)
        except DotfileException as err:
            click.echo(err)


@cli.command()
@click.option('-v', '--verbose', is_flag=True, help='Show executed commands.')
@click.argument('files', nargs=-1, type=click.Path(exists=True))
@pass_repo
def remove(repo, verbose, files):
    """Replace symlink with file."""
    for filename in files:
        try:
            repo.dotfile(py.path.local(filename)).remove(verbose)
            click.echo('removed \'%s\'' % filename)
        except DotfileException as err:
            click.echo(err)


@cli.command()
@click.option('-v', '--verbose', is_flag=True, help='Show all dotfiles.')
@click.option('-c', '--color',   is_flag=True, help='Enable color output.')
@pass_repo
def status(repo, verbose, color):
    """Show all dotfiles in a non-OK state."""

    state_info = {
        'error':    {'char': 'E', 'color': None},
        'conflict': {'char': '!', 'color': None},
        'missing':  {'char': '?', 'color': None},
    }

    if verbose:
        state_info['ok'] = {'char': ' ', 'color': None}

    if color:
        state_info['error']['color'] = 'red'
        state_info['conflict']['color'] = 'magenta'
        state_info['missing']['color'] = 'yellow'

    for dotfile in repo.contents():
        try:
            char = state_info[dotfile.state]['char']
            fg = state_info[dotfile.state]['color']
            click.secho('%c %s' % (char, dotfile), fg=fg)
        except KeyError:
            continue


@cli.command()
@click.option('-v', '--verbose', is_flag=True, help='Show executed commands.')
@click.argument('files', nargs=-1, type=click.Path())
@pass_repo
def link(repo, verbose, files):
    """Create missing symlinks."""
    # TODO: no files should be interpreted as all files with confirmation
    for filename in files:
        try:
            repo.dotfile(py.path.local(filename)).link(verbose)
            click.echo('linked \'%s\'' % filename)
        except DotfileException as err:
            click.echo(err)


@cli.command()
@click.option('-v', '--verbose', is_flag=True, help='Show executed commands.')
@click.argument('files', nargs=-1, type=click.Path(exists=True))
@pass_repo
def unlink(repo, verbose, files):
    """Remove existing symlinks."""
    # TODO: no files should be interpreted as all files with confirmation
    for filename in files:
        try:
            repo.dotfile(py.path.local(filename)).unlink(verbose)
            click.echo('unlinked \'%s\'' % filename)
        except DotfileException as err:
            click.echo(err)
