import py
import os
import click
import errno
from operator import attrgetter


DEFAULT_HOME = os.path.expanduser('~/')
DEFAULT_REPO = os.path.expanduser('~/Dotfiles')


class Repository(object):
    """A repository is a directory that contains dotfiles.

    :param repodir: the location of the repository directory
    :param homedir: the location of the home directory (primarily for testing)
    """

    def __init__(self, repodir, homedir):
        self.repodir = repodir
        self.homedir = homedir

    def __str__(self):
        """Convert repository contents to human readable form."""
        return ''.join('%s\n' % item for item in self.contents()).rstrip()

    def __repr__(self):
        return '<Repository %r>' % self.repodir

    def expected_name(self, target):
        """Given a repository target, return the expected symlink name."""
        return py.path.local("%s/.%s" % (self.homedir, target.basename))

    def contents(self):
        """Given a repository path, discover all existing dotfiles."""
        contents = []
        self.repodir.ensure(dir=1)
        for target in self.repodir.listdir():
            target = py.path.local(target)
            contents.append(Dotfile(self.expected_name(target), target))
        return sorted(contents, key=attrgetter('name'))


class Dotfile(object):
    """An configuration file managed within a repository.

    :param name: name of the symlink in the home directory (~/.vimrc)
    :param target: where the symlink should point to (~/Dotfiles/vimrc)
    """

    def __init__(self, name, target):
        self.name = name
        self.target = target

    def __str__(self):
        return self.name.basename

    def __repr__(self):
        return '<Dotfile %r>' % self.name

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

    def add(self):
        if self.target.check(exists=1):
            raise OSError(errno.EEXIST, self.target)
        self.name.move(self.target)
        self.link()

    def remove(self):
        if self.target.check(exists=0):
            raise OSError(errno.ENOENT, self.target)
        self.name.remove()
        self.target.move(self.name)

    def link(self):
        self.name.mksymlinkto(self.target)

    def unlink(self):
        self.name.remove()


pass_repo = click.make_pass_decorator(Repository)


@click.group(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('--home-directory', type=click.Path(), default=DEFAULT_HOME,
              show_default=True)
@click.option('--repository', type=click.Path(), default=DEFAULT_REPO,
              show_default=True)
@click.version_option()
@click.pass_context
def cli(ctx, home_directory, repository):
    """Dotfiles is a tool to make managing your dotfile symlinks in $HOME easy,
    allowing you to keep all your dotfiles in a single directory.
    """
    ctx.obj = Repository(py.path.local(repository),
                         py.path.local(home_directory))


@cli.command()
@click.argument('files', nargs=-1, type=click.Path(exists=True))
@pass_repo
def add(repo, files):
    """Add dotfiles to a repository."""
    for filename in files:
        filename = py.path.local(filename)
        click.echo('Dotfile(%s, %s).add()' % (
            filename, repo.expected_name(filename)))


@cli.command()
@click.argument('files', nargs=-1, type=click.Path(exists=True))
@pass_repo
def remove(repo, files):
    """Remove dotfiles from a repository."""
    for filename in files:
        filename = py.path.local(filename)
        click.echo('Dotfile(%s, %s).remove()' % (
            filename, repo.expected_name(filename)))


@cli.command()
@click.option('-a', '--all',   is_flag=True, help='Show all dotfiles.')
@click.option('-c', '--color', is_flag=True, help='Enable color output.')
@pass_repo
def status(repo, all, color):
    """Show all dotfiles in a non-OK state."""

    state_info = {
        'error':    {'char': 'E', 'color': None},
        'conflict': {'char': '!', 'color': None},
        'missing':  {'char': '?', 'color': None},
    }

    if all:
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
@click.argument('files', nargs=-1, type=click.Path())
@pass_repo
def link(repo, files):
    """Create any missing symlinks."""
    for filename in files:
        click.echo('Dotfile(%s).link()' % filename)


@cli.command()
@click.argument('files', nargs=-1, type=click.Path(exists=True))
@pass_repo
def unlink(repo, files):
    """Remove existing symlinks."""
    for filename in files:
        click.echo('Dotfile(%s).unlink()' % filename)
