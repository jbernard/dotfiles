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

DEFAULT_REPO = os.path.expanduser('~/Dotfiles')


def parse_args():

    parser = OptionParser(usage="%prog ACTION [OPTION...] [FILE...]")

    parser.set_defaults(config=os.path.expanduser("~/.dotfilesrc"))
    parser.set_defaults(ignore=[])
    parser.set_defaults(externals={})

    parser.add_option("-v", "--version", action="store_true",
            dest="show_version", default=False,
            help="show version number and exit")

    parser.add_option("-f", "--force", action="store_true", dest="force",
            default=False, help="ignore unmanaged dotfiles (use with --sync)")

    # OptionParser expands ~ constructions
    parser.add_option("-R", "--repo", type="string", dest="repo",
            help="set repository location (default is %s)" % DEFAULT_REPO)

    parser.add_option("-p", "--prefix", type="string", dest="prefix",
            help="set prefix character (default is None)")

    parser.add_option("-C", "--config", type="string", dest="config",
            help="set configuration file location (default is ~/.dotfilesrc)")

    parser.add_option("-H", "--home", type="string", dest="home",
            help="set home directory location (default is ~/)")

    action_group = OptionGroup(parser, "Actions")

    action_group.add_option("-a", "--add", action="store_const", dest="action",
            const="add", help="add dotfile(s) to the repository")

    action_group.add_option("-c", "--check", action="store_const",
            dest="action", const="check", help="check dotfiles repository")

    action_group.add_option("-l", "--list", action="store_const",
            dest="action", const="list",
            help="list currently managed dotfiles")

    action_group.add_option("-r", "--remove", action="store_const",
            dest="action", const="remove",
            help="remove dotfile(s) from the repository")

    action_group.add_option("-s", "--sync", action="store_const",
            dest="action", const="sync", help="update dotfile symlinks")

    action_group.add_option("-m", "--move", action="store_const",
            dest="action", const="move", help="move dotfiles repository to " \
            "another location")

    parser.add_option_group(action_group)

    (opts, args) = parser.parse_args()

    # Skip checking if the repository exists here. The user may have specified
    # a command line argument or a configuration file, which will be examined
    # next.

    return (opts, args)


def main():

    (opts, args) = parse_args()

    if opts.show_version:
        print 'dotfiles v%s' % core.__version__
        exit(0)

    config_defaults = {
            'repository':   opts.repo,
            'prefix':       opts.prefix,
            'ignore':       opts.ignore,
            'externals':    opts.externals}

    parser = ConfigParser.SafeConfigParser(config_defaults)
    parser.read(opts.config)

    if 'dotfiles' in parser.sections():

        if not opts.repo and parser.get('dotfiles', 'repository'):
            opts.repo = parser.get('dotfiles', 'repository')
            if opts.action == 'move':
                # TODO: update the configuration file after the move
                print 'Remember to update the repository location ' \
                      'in your configuration file (%s).' % (opts.config)

        if not opts.prefix and parser.get('dotfiles', 'prefix'):
            opts.prefix = parser.get('dotfiles', 'prefix')

        if not opts.ignore and parser.get('dotfiles', 'ignore'):
            opts.ignore = eval(parser.get('dotfiles', 'ignore'))

        if not opts.externals and parser.get('dotfiles', 'externals'):
            opts.externals = eval(parser.get('dotfiles', 'externals'))

    if not opts.repo:
        opts.repo = DEFAULT_REPO

    opts.repo = os.path.realpath(os.path.expanduser(opts.repo))

    if not opts.prefix:
        opts.prefix = ''

    if not os.path.exists(opts.repo):
        print 'Error: Could not find dotfiles repository \"%s\"' % (opts.repo)
        if opts.repo == DEFAULT_REPO:
            missing_default_repo()
        exit(-1)

    if not opts.action:
        print "Error: An action is required. Type 'dotfiles -h' to see detailed usage information."
        exit(-1)

    dotfiles = core.Dotfiles(home='~/', repo=opts.repo, prefix=opts.prefix,
            ignore=opts.ignore, externals=opts.externals)

    if opts.action in ['list', 'check']:
        getattr(dotfiles, opts.action)()

    elif opts.action in ['add', 'remove']:
        getattr(dotfiles, opts.action)(args)

    elif opts.action == 'sync':
        dotfiles.sync(opts.force)

    elif opts.action == 'move':
        if len(args) > 1:
            print "Error: Move cannot handle multiple targets."
            exit(-1)
        if opts.repo != args[0]:
            dotfiles.move(args[0])

    else:
        print "Error: Something truly terrible has happened."
        exit(-1)


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

Type 'dotfiles -h' to see detailed usage information.""".format(DEFAULT_REPO)
