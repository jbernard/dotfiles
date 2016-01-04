import py
import os
import click
import errno
from operator import attrgetter


DEFAULT_HOME = os.path.expanduser('~/')
DEFAULT_REPO = os.path.expanduser('~/Dotfiles')


def unique_suffix(path_a, path_b):
    discard = len(str(path_a.common(path_b))) + 1
    return (str(path_a)[discard:], str(path_b)[discard:])


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
        Dotfile(filename, repo.target(filename)).add()


@cli.command()
@click.option('-v', '--verbose', is_flag=True, help='Show dotfile state.')
@pass_repo
def list(repo, verbose):
    """Show the contents of a repository."""
    dotfiles = repo.contents()
    if not dotfiles:
        click.echo('[no dotfiles found]')
    for dotfile in dotfiles:
        if (verbose):
            click.echo('%-18s (%s)' % (dotfile, dotfile.state))
        else:
            click.echo('%s' % dotfile)


@cli.command()
@click.argument('files', nargs=-1, type=click.Path(exists=True))
@pass_repo
def remove(repo, files):
    """Remove dotfiles from a repository."""
    for filename in files:
        Dotfile(filename, repo.target(filename)).remove()


@cli.command()
@click.option('-c', '--color', is_flag=True, help='Enable color.')
@click.option('-s', '--short', is_flag=True, help='Show terse output.')
@pass_repo
def status(repo, color, short):
    """Show all dotifles in a non-OK state."""

    states = {
        'error':    {'char': 'E', 'color': 'red'},
        'conflict': {'char': '!', 'color': 'magenta'},
        'missing':  {'char': '?', 'color': 'yellow'},
    }

    if not short:
        click.echo('long output not yet implemeted, using --short for now')

    dotfiles = repo.contents()
    for dotfile in dotfiles:
        try:
            state_str = states[dotfile.state]['char']
            color_str = states[dotfile.state]['color']
            if color:
                click.secho('%s %s' % (state_str, dotfile), fg=color_str)
            else:
                click.echo('%s %s' % (state_str, dotfile))
        except KeyError:
            continue


@cli.command()
@click.argument('files', nargs=-1, type=click.Path())
@pass_repo
def sync(repo, files):
    """Create any missing symlinks."""
    for filename in files:
        repo.sync(filename)

    # TODO: path need not exist...


@cli.command()
@click.argument('files', nargs=-1, type=click.Path(exists=True))
@pass_repo
def unsync(repo, files):
    """Remove existing symlinks."""
    for filename in files:
        repo.unsync(filename)
