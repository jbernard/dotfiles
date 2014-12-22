import os
try:
    import ConfigParser as configparser
except ImportError:
    import configparser
from optparse import OptionParser, OptionGroup

from .utils import compare_path, realpath_expanduser
from .core import Dotfiles as Repository
from . import __version__


CONFIG_FILE = '.dotfilesrc'


# Users can define configuration at several different levels to overlay
# specific configuration for a particular repository.  These settings are
# accumulated and passed to the Repository constructor once parsing has
# completed.
repo_settings = {
    'path': Repository.defaults['path'],
    'prefix': Repository.defaults['prefix'],
    'ignore': Repository.defaults['ignore'],
    'homedir': Repository.defaults['homedir'],
    'packages': Repository.defaults['packages'],
    'externals': Repository.defaults['externals'],
}


def missing_default_repo():
    """Print a helpful message when the default repository is missing.

    For a first-time user, this is the first message they're likely to see, so
    it should be as helpful as possible.
    """

    print("""
If this is your first time running dotfiles, you must first create
a repository.  By default, dotfiles will look for '{0}'.
Something like:

    $ mkdir {0}

is all you need to do.  If you don't like the default, you can put your
repository wherever you like.  You have two choices once you've created your
repository.  You can specify the path to the repository on the command line
using the '-R' flag.  Alternatively, you can create a configuration file at
'~/{1}' and place the path to your repository in there.  The contents would
look like:

    [dotfiles]
    repository = {0}

Type 'dotfiles -h' to see detailed usage information.""".format
          (repo_settings['path'], CONFIG_FILE))


def add_global_flags(parser):
    parser.add_option("-v", "--version",
                      action="store_true", dest="show_version", default=False,
                      help="show version number and exit")

    parser.add_option("-f", "--force",
                      action="store_true", dest="force", default=False,
                      help="overwrite colliding dotfiles (use with --sync)")

    parser.add_option("-R", "--repo",
                      type="string", dest="repository",
                      help="set repository location (default: %s)" % (
                          repo_settings['path']))

    parser.add_option("-p", "--prefix",
                      type="string", dest="prefix",
                      help="set prefix character (default: %s)" % (
                          None if not repo_settings['prefix'] else
                          repo_settings['prefix']))

    parser.add_option("-C", "--config",
                      type="string", dest="config_file",
                      help="set configuration file (default: ~/%s)" % (
                          CONFIG_FILE))

    parser.add_option("-H", "--home",
                      type="string", dest="homedir",
                      help="set home directory location (default: %s)" % (
                          repo_settings['homedir']))

    parser.add_option("-d", "--dry-run",
                      action="store_true", default=False,
                      help="don't modify anything, just print commands")

    parser.add_option("-n", "--no-dot-prefix",
                      action="store_true", default=False,
                      help="don't prefix symlinks in target directory with a '.'")


def add_action_group(parser):
    action_group = OptionGroup(parser, "Actions")

    action_group.add_option("-a", "--add",
                            action="store_const", dest="action", const="add",
                            help="add dotfile(s) to the repository")

    action_group.add_option("-c", "--check",
                            action="store_const", dest="action", const="check",
                            help="check for broken and unsynced dotfiles")

    action_group.add_option("-l", "--list",
                            action="store_const", dest="action", const="list",
                            help="list currently managed dotfiles")

    action_group.add_option("-r", "--remove",
                            action="store_const", dest="action",
                            const="remove",
                            help="remove dotfile(s) from the repository")

    action_group.add_option("-s", "--sync",
                            action="store_const", dest="action", const="sync",
                            help="update dotfile symlinks")

    action_group.add_option("-m", "--move",
                            action="store_const", dest="action", const="move",
                            help="move (rename) dotfiles repository")

    parser.add_option_group(action_group)


def parse_args():

    parser = OptionParser(usage="%prog ACTION [OPTION...] [FILE...]")

    add_global_flags(parser)
    add_action_group(parser)

    (opts, args) = parser.parse_args()

    if opts.show_version:
        print('dotfiles v%s' % __version__)
        exit(0)

    if not opts.action:
        print("Error: An action is required. Type 'dotfiles -h' to see "
              "detailed usage information.")
        exit(-1)

    return (opts, args)


def parse_config(config_file):
    parser = configparser.SafeConfigParser()
    parser.read(os.path.expanduser(config_file))

    opts = dict()

    for entry in ('repository', 'prefix'):
        try:
            opts[entry] = parser.get('dotfiles', entry)
        except configparser.NoOptionError:
            pass
        except configparser.NoSectionError:
            break

    for entry in ('ignore', 'externals', 'packages'):
        try:
            opts[entry] = eval(parser.get('dotfiles', entry))
        except configparser.NoOptionError:
            pass
        except configparser.NoSectionError:
            break

    return opts


def dispatch(repo, opts, args):

    # TODO: handle/pass dry_run

    if opts.action in ['list', 'check']:
        getattr(repo, opts.action)()

    elif opts.action in ['add', 'remove']:
        getattr(repo, opts.action)(args)

    elif opts.action == 'sync':
        getattr(repo, opts.action)(files=args, force=opts.force)

    elif opts.action == 'move':
        if len(args) > 1:
            print("Error: Move cannot handle multiple targets.")
            exit(-1)
        repo.move(args[0])

    else:
        print("Error: Something truly terrible has happened.")
        exit(-1)


def check_repository_exists():
    if not os.path.exists(repo_settings['path']):
        print('Error: Could not find dotfiles repository \"%s\"' % (
            repo_settings['path']))
        if compare_path(repo_settings['path'], Repository.defaults['path']):
            missing_default_repo()
        exit(-1)


def update_settings(opts, key):
    global repo_settings

    value = opts.get(key)
    if value:
        repo_settings[key].update(value)


def main():

    global repo_settings

    (cli_opts, args) = parse_args()

    repo_settings['homedir'] = realpath_expanduser(
        cli_opts.homedir or repo_settings['homedir'])

    config_opts = parse_config(cli_opts.config_file or '~/%s' % CONFIG_FILE)

    repo_settings['path'] = realpath_expanduser(
        cli_opts.repository or
        config_opts.get('repository') or
        repo_settings['path'])

    check_repository_exists()

    update_settings(config_opts, 'ignore')
    update_settings(config_opts, 'externals')
    update_settings(config_opts, 'packages')

    repo_config_file = os.path.join(repo_settings['path'], CONFIG_FILE)
    repo_config_opts = parse_config(repo_config_file)

    repo_settings['prefix'] = (cli_opts.prefix or
                               repo_config_opts.get('prefix') or
                               config_opts.get('prefix') or
                               repo_settings['prefix'])
    repo_settings['no_dot_prefix'] = cli_opts.no_dot_prefix

    update_settings(repo_config_opts, 'ignore')
    update_settings(repo_config_opts, 'externals')
    update_settings(repo_config_opts, 'packages')

    repo = Repository(**repo_settings)

    dispatch(repo, cli_opts, args)
