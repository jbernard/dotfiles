import sys
import click

from . import __version__
from .repository import Repository


pass_repo = click.make_pass_decorator(Repository)


@click.group()
@click.option('-r', '--repository', type=click.Path(), default='~/Dotfiles',
              help='Sets the repository folder location.')
@click.pass_context
def main(ctx, repository):
    """Dotfiles is a tool to make managing your dotfile symlinks in $HOME easy,
    allowing you to keep all your dotfiles in a single directory.

    The default repository is ~/Dotfiles unless specified otherwise and will be
    created on demand.  If you prefer a different location, you can put your
    repository wherever you like using the --repository flag or using the
    ~/.dotfilesrc configuration file with a contents of:

    \b
    [dotfiles]
    repository = ~/Dotfiles
    """
    ctx.obj = Repository(repository)


@main.command()
@pass_repo
def check(repo):
    """Shows any broken or unsyned dotfiles."""
    list = repo.check()
    if list:
        click.echo_via_pager(list)
        sys.exit(1)


@main.command()
@pass_repo
def status(repo):
    """Shows the status of each dotfile."""
    click.echo_via_pager(repo.status())


@main.command()
def version():
    """Shows the current version number."""
    click.echo("dotfiles v%s" % __version__)
