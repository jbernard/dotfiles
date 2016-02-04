import os
import click

from .repository import Repository
from .exceptions import DotfileException


DEFAULT_DOT = False
DEFAULT_REPO = os.path.expanduser('~/Dotfiles')
DEFAULT_IGNORE_PATTERNS = ['.git', '.hg', '*~']
CONTEXT_SETTINGS = dict(auto_envvar_prefix='DOTFILES',
                        help_option_names=['-h', '--help'])


def get_single_repo(context):
    if len(context.obj) > 1:
        raise click.BadParameter('Must specify exactly one repository.',
                                 param_hint=['-r', '--repo'])
    return context.obj[0]


def confirm(method, files, repo):
    """Return a list of files, or all files if none were specified."""
    if files:
        # user has specified specific files, so we are not assuming all
        return files
    # no files provided, so we assume all files after confirmation
    message = 'Are you sure you want to %s all dotfiles?' % method
    click.confirm(message, abort=True)
    return str(repo).split()


def perform(method, files, repo, debug):
    """Perform an operation on a set of dotfiles."""
    for dotfile in repo.dotfiles(files):
        try:
            getattr(dotfile, method)(debug)
            if not debug:
                msg = '%s%s' % (method, 'd' if method[-1] == 'e' else 'ed')
                click.echo('%s %s' % (msg, dotfile.short_name(repo.homedir)))
        except DotfileException as err:
            click.echo(err)


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('-r', '--repo', type=click.Path(), multiple=True,
              default=[DEFAULT_REPO], show_default=True,
              help='A repository path.')
@click.option('-d', '--dot', is_flag=True, help='Preserve the leading dot.')
@click.version_option(None, '-v', '--version')
@click.pass_context
def cli(ctx, repo, dot):
    """Dotfiles is a tool to make managing your dotfile symlinks in $HOME easy,
    allowing you to keep all your dotfiles in a single directory.
    """
    ctx.obj = []
    for path in repo:
        ctx.obj.append(Repository(path,
                                  ignore_patterns=DEFAULT_IGNORE_PATTERNS,
                                  preserve_leading_dot=dot))


@cli.command()
@click.option('-d', '--debug', is_flag=True,
              help='Show what would be executed.')
@click.argument('files', nargs=-1, type=click.Path(exists=True))
@click.pass_context
def add(ctx, debug, files):
    """Add dotfiles to a repository."""
    repo = get_single_repo(ctx)
    perform('add', files, repo, debug)


@cli.command()
@click.option('-d', '--debug', is_flag=True,
              help='Show what would be executed.')
@click.argument('files', nargs=-1, type=click.Path(exists=True))
@click.pass_context
def remove(ctx, debug, files):
    """Remove dotfiles from a repository."""
    repo = get_single_repo(ctx)
    files = confirm('remove', files, repo)
    perform('remove', files, repo, debug)
    if not debug:
        repo.prune()


@cli.command()
@click.option('-d', '--debug', is_flag=True,
              help='Show what would be executed.')
@click.argument('files', nargs=-1, type=click.Path())
@click.pass_context
def link(ctx, debug, files):
    """Create missing symlinks."""
    repo = get_single_repo(ctx)
    files = confirm('link', files, repo)
    perform('link', files, repo, debug)


@cli.command()
@click.option('-d', '--debug', is_flag=True,
              help='Show what would be executed.')
@click.argument('files', nargs=-1, type=click.Path(exists=True))
@click.pass_context
def unlink(ctx, debug, files):
    """Remove existing symlinks."""
    repo = get_single_repo(ctx)
    files = confirm('unlink', files, repo)
    perform('unlink', files, repo, debug)


@cli.command()
@click.option('-a', '--all',   is_flag=True, help='Show all dotfiles.')
@click.option('-c', '--color', is_flag=True, help='Enable color output.')
@click.pass_context
def status(ctx, all, color):
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

    for repo in ctx.obj:
        if len(ctx.obj) > 1:
            click.secho('%s:' % repo.path)
        for dotfile in repo.contents():
            try:
                name = dotfile.short_name(repo.homedir)
                char = state_info[dotfile.state]['char']
                color = state_info[dotfile.state]['color']
                click.secho('%c %s' % (char, name), fg=color)
            except KeyError:
                continue
