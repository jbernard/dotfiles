import os
import py
import click

from .repository import Repository
from .exceptions import DotfileException


DEFAULT_HOMEDIR = os.path.expanduser('~/')
DEFAULT_REPO_PATH = os.path.expanduser('~/Dotfiles')
DEFAULT_REPO_IGNORE = ['.git']

pass_repo = click.make_pass_decorator(Repository)


def perform(repo, debug, files, method):
    for dotfile in repo.dotfiles(files):
        try:
            getattr(dotfile, method)(debug)
            if not debug:
                click.echo('%sed %s' % (method,
                                        dotfile.short_name(repo.homedir)))
        except DotfileException as err:
            click.echo(err)


@click.group(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-r', '--repository', type=click.Path(), show_default=True,
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
@click.option('-d', '--debug', is_flag=True,
              help='Show commands that would be executed.')
@click.argument('files', nargs=-1, type=click.Path(exists=True))
@pass_repo
def add(repo, debug, files):
    """Replace file with symlink."""
    perform(repo, debug, files, 'add')


@cli.command()
@click.option('-d', '--debug', is_flag=True,
              help='Show commands that would be executed.')
@click.argument('files', nargs=-1, type=click.Path(exists=True))
@pass_repo
def remove(repo, debug, files):
    """Replace symlink with file."""
    perform(repo, debug, files, 'remove')


@cli.command()
@click.option('-a', '--all',   is_flag=True, help='Show all dotfiles.')
@click.option('-c', '--color', is_flag=True, help='Enable color output.')
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


@cli.command()
@click.option('-v', '--verbose', is_flag=True, help='Show executed commands.')
@click.argument('files', nargs=-1, type=click.Path())
@pass_repo
def link(repo, verbose, files):
    """Create missing symlinks."""
    # TODO: no files should be interpreted as all files
    raise RuntimeError('Not implemented yet')


@cli.command()
@click.option('-v', '--verbose', is_flag=True, help='Show executed commands.')
@click.argument('files', nargs=-1, type=click.Path(exists=True))
@pass_repo
def unlink(repo, verbose, files):
    """Remove existing symlinks."""
    # TODO: no files should be interpreted as all files with confirmation
    raise RuntimeError('Not implemented yet')
