import os
import copy
import click
import py.path

try:
    import ConfigParser as configparser
except ImportError:
    import configparser

from .repository import Repository
from .exceptions import DotfileException


DEFAULT_DOT = False
DEFAULT_REPO = os.path.expanduser('~/Dotfiles')
DEFAULT_IGNORE_PATTERNS = ['README*', '.git', '.hg', '*~']

CONTEXT_SETTINGS = dict(auto_envvar_prefix='DOTFILES',
                        help_option_names=['-h', '--help'])


class Config(object):

    def __init__(self, paths):
        self.settings = self.parse_config({})

        # repositories specified on the command line take precedence
        if paths:
            self.settings.update({'repositories': str(set(paths))})

        # assume default repository at this point
        if 'repositories' not in self.settings:
            self.settings.update({'repositories': str([DEFAULT_REPO])})
        if 'ignore_patterns' not in self.settings:
            self.settings.update({'ignore_patterns':
                                  str(DEFAULT_IGNORE_PATTERNS)})

        # TODO: apply repository configuration, if available

    def parse_config(self, settings):
        settings = copy.deepcopy(settings)
        cfg = os.path.join(click.get_app_dir('Dotfiles'), 'config.ini')
        parser = configparser.RawConfigParser()
        parser.read([cfg])
        try:
            settings.update(parser.items('dotfiles'))
        except configparser.NoSectionError:
            pass
        return settings

    def _get_setting(self, setting):
        return eval(self.settings[setting])

    @property
    def repositories(self):
        return self._get_setting('repositories')

    @property
    def ignore_patterns(self):
        return self._get_setting('ignore_patterns')


class Repositories(object):

    def __init__(self, paths, dot):
        config = Config(paths)

        self.repos = []
        # for path in eval(config.settings['repositories']):
        for path in config.repositories:
            # will this ever change, why is this in the loop?
            ignore_patterns = config.ignore_patterns
            self.repos.append(
                Repository(py.path.local(path, expanduser=True),
                           ignore_patterns=ignore_patterns,
                           preserve_leading_dot=dot))

    def __len__(self):
        return len(self.repos)

    def __getitem__(self, index):
        return self.repos[index]


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
repo_help = 'A repository path.'
dot_help = 'Preserve the leading dot.'

@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('-r', '--repo', type=click.Path(), multiple=True, help=repo_help)
@click.option('-d', '--dot', is_flag=True, help=dot_help)
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
