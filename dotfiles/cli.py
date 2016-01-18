import os
import py
import click

from .repository import Repository
from .exceptions import DotfileException


DEFAULT_REPODIR = os.path.expanduser('~/Dotfiles')


def confirm(method, files, repo):
    if files:
        return files
    message = 'Are you sure you want to %s all dotfiles?' % method
    click.confirm(message, abort=True)
    return str(repo).split()


def perform(method, files, repo, debug):
    for dotfile in repo.dotfiles(files):
        try:
            getattr(dotfile, method)(debug)
            if not debug:
                msg = '%s%s' % (method, 'd' if method[-1] == 'e' else 'ed')
                click.echo('%s %s' % (msg, dotfile.short_name(repo.homedir)))
        except DotfileException as err:
            click.echo(err)


pass_repo = click.make_pass_decorator(Repository)


@click.group(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-r', '--repo', type=click.Path(), show_default=True,
              default=DEFAULT_REPODIR, envvar='DOTFILES_REPO')
@click.version_option()
@click.pass_context
def cli(ctx, repo):
    """Dotfiles is a tool to make managing your dotfile symlinks in $HOME easy,
    allowing you to keep all your dotfiles in a single directory.

    The following environment variables are recognized at runtime:

    \b
    DOTFILES_REPO:  Set this to the location of your repository.
    DOTFILES_COLOR: Set this to 'True' to enable color output.
    """
    ctx.obj = Repository(py.path.local(py.path.local(repo)))


@cli.command()
@click.option('-d', '--debug', is_flag=True,
              help='Show commands that would be executed.')
@click.argument('files', nargs=-1, type=click.Path(exists=True))
@pass_repo
def add(repo, debug, files):
    """Replace file with symlink."""
    perform('add', files, repo, debug)


@cli.command()
@click.option('-d', '--debug', is_flag=True,
              help='Show commands that would be executed.')
@click.argument('files', nargs=-1, type=click.Path(exists=True))
@pass_repo
def remove(repo, debug, files):
    """Replace symlink with file."""
    files = confirm('remove', files, repo)
    perform('remove', files, repo, debug)
    if not debug:
        repo.prune()


@cli.command()
@click.option('-d', '--debug', is_flag=True,
              help='Show commands that would be executed.')
@click.argument('files', nargs=-1, type=click.Path())
@pass_repo
def link(repo, debug, files):
    """Create missing symlinks."""
    files = confirm('link', files, repo)
    perform('link', files, repo, debug)


@cli.command()
@click.option('-d', '--debug', is_flag=True,
              help='Show commands that would be executed.')
@click.argument('files', nargs=-1, type=click.Path(exists=True))
@pass_repo
def unlink(repo, debug, files):
    """Remove existing symlinks."""
    files = confirm('unlink', files, repo)
    perform('unlink', files, repo, debug)


@cli.command()
@click.option('-a', '--all',   is_flag=True, help='Show all dotfiles.')
@click.option('-c', '--color', is_flag=True, help='Enable color output.',
              envvar='DOTFILES_COLOR')
@pass_repo
def status(repo, all, color):
    """Show all dotfiles in a non-OK state."""
    state_info = {
        'error':    {'char': 'E', 'color': None},
        'missing':  {'char': '?', 'color': None},
        'conflict': {'char': '!', 'color': None},
    }

    if all:
        state_info['ok'] = {'char': ' ', 'color': None}

    if color:
        state_info['error']['color'] = 'red'
        state_info['missing']['color'] = 'yellow'
        state_info['conflict']['color'] = 'magenta'

    for dotfile in repo.contents():
        try:
            name = dotfile.short_name(repo.homedir)
            char = state_info[dotfile.state]['char']
            color = state_info[dotfile.state]['color']
            click.secho('%c %s' % (char, name), fg=color)
        except KeyError:
            continue
