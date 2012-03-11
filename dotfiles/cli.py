# -*- coding: utf-8 -*-

"""
dotfiles.cli

This module provides the CLI interface to dotfiles.
"""

from __future__ import absolute_import

import os
from . import core
import ConfigParser
from optparse import OptionParser, OptionGroup

defaults = {
        'prefix': '',
        'homedir': '~/',
        'repository': '~/Dotfiles',
        'config_file': '~/.dotfilesrc'}

settings = {
        'prefix': None,
        'homedir': None,
        'repository': None,
        'config_file': None,
        'ignore': set(['.dotfilesrc']),
        'externals': dict()}


def missing_default_repo():
    """Print a helpful message when the default repository is missing."""

    print """
If this is your first time running dotfiles, you must first create
a repository.  By default, dotfiles will look for '{0}'.
Something like:

    $ mkdir {0}

is all you need to do.  If you don't like the default, you can put your
repository wherever you like.  You have two choices once you've created your
repository.  You can specify the path to the repository on the command line
using the '-R' flag.  Alternatively, you can create a configuration file at
'~/.dotfilesrc' and place the path to your repository in there.  The contents
would look like:

    [dotfiles]
    repository = {0}

Type 'dotfiles -h' to see detailed usage information.""".format(
        defaults['repository'])


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
                defaults['repository']))

    parser.add_option("-p", "--prefix",
            type="string", dest="prefix",
            help="set prefix character (default: %s)" % (
                "None" if not defaults['prefix'] else defaults['prefix']))

    parser.add_option("-C", "--config",
            type="string", dest="config_file",
            help="set configuration file location (default: %s)" % (
                defaults['config_file']))

    parser.add_option("-H", "--home",
            type="string", dest="homedir",
            help="set home directory location (default: %s)" % (
                defaults['homedir']))


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
            action="store_const", dest="action", const="remove",
            help="remove dotfile(s) from the repository")

    action_group.add_option("-s", "--sync",
            action="store_const", dest="action", const="sync",
            help="update dotfile symlinks")

    action_group.add_option("-m", "--move",
            action="store_const", dest="action", const="move",
            help="move dotfiles repository to another location")

    parser.add_option_group(action_group)


def parse_args():

    parser = OptionParser(usage="%prog ACTION [OPTION...] [FILE...]")

    add_global_flags(parser)
    add_action_group(parser)

    (opts, args) = parser.parse_args()

    if opts.show_version:
        print 'dotfiles v%s' % core.__version__
        exit(0)

    if not opts.action:
        print "Error: An action is required. Type 'dotfiles -h' to see " \
              "detailed usage information."
        exit(-1)

    return (opts, args)


def parse_config(config_file):

    parser = ConfigParser.SafeConfigParser()
    parser.read(config_file)

    opts = {'repository': None,
            'prefix': None,
            'ignore': set(),
            'externals': dict()}

    for entry in ('repository', 'prefix'):
        try:
            opts[entry] = parser.get('dotfiles', entry)
        except ConfigParser.NoOptionError:
            pass
        except ConfigParser.NoSectionError:
            break

    for entry in ('ignore', 'externals'):
        try:
            opts[entry] = eval(parser.get('dotfiles', entry))
        except ConfigParser.NoOptionError:
            pass
        except ConfigParser.NoSectionError:
            break

    return opts


def dispatch(dotfiles, action, force, args):
    if action in ['list', 'check']:
        getattr(dotfiles, action)()
    elif action in ['add', 'remove']:
        getattr(dotfiles, action)(args)
    elif action == 'sync':
        dotfiles.sync(force)
    elif action == 'move':
        if len(args) > 1:
            print "Error: Move cannot handle multiple targets."
            exit(-1)
        dotfiles.move(args[0])
    else:
        print "Error: Something truly terrible has happened."
        exit(-1)


def compare_path(path1, path2):
    return (os.path.realpath(os.path.expanduser(path1)) ==
            os.path.realpath(os.path.expanduser(path2)))


def realpath(path):
    return os.path.realpath(os.path.expanduser(path))


def check_repository_exists():
    if not os.path.exists(settings['repository']):
        print 'Error: Could not find dotfiles repository \"%s\"' % (
                settings['repository'])
        if compare_path(settings['repository'], defaults['repository']):
            missing_default_repo()
        exit(-1)


def update_settings(opts, key):
    global settings

    settings[key].update(opts[key])


def main():

    global settings

    (cli_opts, args) = parse_args()

    settings['homedir'] = realpath(cli_opts.homedir or defaults['homedir'])
    settings['config_file'] = realpath(cli_opts.config_file or
            defaults['config_file'])

    config_opts = parse_config(settings['config_file'])

    settings['repository'] = realpath(cli_opts.repository or
            config_opts['repository'] or defaults['repository'])

    check_repository_exists()

    update_settings(config_opts, 'ignore')
    update_settings(config_opts, 'externals')

    repo_config_file = os.path.join(settings['repository'], '.dotfilesrc')
    repo_config_opts = parse_config(repo_config_file)

    settings['prefix'] = (cli_opts.prefix or
                          repo_config_opts['prefix'] or
                          config_opts['prefix'] or
                          defaults['prefix'])

    update_settings(repo_config_opts, 'ignore')
    update_settings(repo_config_opts, 'externals')

    dotfiles = core.Dotfiles(**settings)

    dispatch(dotfiles, cli_opts.action, cli_opts.force, args)
