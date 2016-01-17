import os
import py
import click

from .repository import Repository
from .exceptions import DotfileException


DEFAULT_HOMEDIR = os.path.expanduser('~/')
DEFAULT_REPO_PATH = os.path.expanduser('~/Dotfiles')
DEFAULT_REPO_IGNORE = ['.git']

pass_repo = click.make_pass_decorator(Repository)


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
    for dotfile in repo.dotfiles(files):
        dotfile.add(debug)

        # try:
        #     repo.dotfile(py.path.local(filename)).add(debug)
        #     if not debug:
        #         click.echo('added \'%s\'' % filename)
        # except DotfileException as err:
        #     click.echo(err)


@cli.command()
@click.option('-d', '--debug', is_flag=True,
              help='Show commands that would be executed.')
@click.argument('files', nargs=-1, type=click.Path(exists=True))
@pass_repo
def remove(repo, debug, files):
    """Replace symlink with file."""
    for filename in files:
        try:
            repo.dotfile(py.path.local(filename)).remove(debug)
            if not debug:
                click.echo('removed \'%s\'' % filename)
        except DotfileException as err:
            click.echo(err)


def show_dotfile(homedir, char, dotfile, color):
    display_name = homedir.bestrelpath(dotfile.name)
    click.secho('%c %s' % (char, display_name), fg=color)


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
            char = state_info[dotfile.state]['char']
            color = state_info[dotfile.state]['color']
            show_dotfile(repo.homedir, char, dotfile, color)
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
