import click

from .exceptions import DotfileException
from .repository import Repositories, DEFAULT_PATH, DEFAULT_REMOVE_LEADING_DOT


def get_single_repo(repos):
    if len(repos) > 1:
        raise click.BadParameter('Must specify exactly one repository.',
                                 param_hint=['-r', '--repo'])
    return repos[0]


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


pass_repos = click.make_pass_decorator(Repositories)
CONTEXT_SETTINGS = dict(auto_envvar_prefix='DOTFILES',
                        help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('--repo', '-r', type=click.Path(), multiple=True,
              help='A repository path. Default: %s' % (DEFAULT_PATH))
@click.option('--dot/--no-dot', '-d/-D', default=None,
              help='Whether to remove the leading dot. Default: %s' % (
                  DEFAULT_REMOVE_LEADING_DOT))
@click.version_option(None, '-v', '--version')
@click.pass_context
def cli(ctx, repo, dot):
    """Dotfiles is a tool to make managing your dotfile symlinks in $HOME easy,
    allowing you to keep all your dotfiles in a single directory.
    """
    ctx.obj = Repositories(repo, dot)


@cli.command()
@click.option('-d', '--debug', is_flag=True,
              help='Show what would be executed.')
@click.argument('files', nargs=-1, type=click.Path(exists=True))
@pass_repos
def add(repos, debug, files):
    """Add dotfiles to a repository."""
    repo = get_single_repo(repos)
    perform('add', files, repo, debug)


@cli.command()
@click.option('-d', '--debug', is_flag=True,
              help='Show what would be executed.')
@click.argument('files', nargs=-1, type=click.Path(exists=True))
@pass_repos
def remove(repos, debug, files):
    """Remove dotfiles from a repository."""
    repo = get_single_repo(repos)
    files = confirm('remove', files, repo)
    perform('remove', files, repo, debug)
    if not debug:
        repo.prune()


@cli.command()
@click.option('-d', '--debug', is_flag=True,
              help='Show what would be executed.')
@click.argument('files', nargs=-1, type=click.Path())
@pass_repos
def link(repos, debug, files):
    """Create missing symlinks."""
    # TODO: allow all repos?  It *could* be fine...
    repo = get_single_repo(repos)
    files = confirm('link', files, repo)
    perform('link', files, repo, debug)


@cli.command()
@click.option('-d', '--debug', is_flag=True,
              help='Show what would be executed.')
@click.argument('files', nargs=-1, type=click.Path(exists=True))
@pass_repos
def unlink(repos, debug, files):
    """Remove existing symlinks."""
    repo = get_single_repo(repos)
    files = confirm('unlink', files, repo)
    perform('unlink', files, repo, debug)


@cli.command()
@click.option('-a', '--all',   is_flag=True, help='Show all dotfiles.')
@click.option('-c', '--color', is_flag=True, help='Enable color output.')
@pass_repos
def status(repos, all, color):
    """Show all dotfiles in a non-OK state.

    Legend:

      ?: missing  !: conflict  E: error

    Meaning:

      * Missing: A dotfile in the repository is not present in your home
      directory.

      * Conflict: A dotfile in the repository is different from the file
      in your home directory.

      * Error: A dotfile expected in the repository is not present.  You
      should never see this."""

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

    for repo in repos:
        if len(repos) > 1:
            click.secho('%s:' % repo.path)
        for dotfile in repo.contents():
            try:
                name = dotfile.short_name(repo.homedir)
                char = state_info[dotfile.state]['char']
                color = state_info[dotfile.state]['color']
                click.secho('%c %s' % (char, name), fg=color)
            except KeyError:
                continue
