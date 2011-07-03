# -*- coding: utf-8 -*-

"""
dotfiles.cli

This module provides the CLI interface to dotfiles.
"""

import os
from . import core
import ConfigParser
from optparse import OptionParser, OptionGroup


USAGE = "Usage: %prog ACTION [OPTION...] [FILE...]"

NO_REPO_MESSAGE = """Could not find dotfiles repository \"%s\"

If this is your first time running dotfiles, you must first create a
repository.  By default, dotfiles will look for '~/Dotfiles'. Something like:

    $ mkdir ~/Dotfiles

is all you need to do. If you don't like the default, you can put your
repository wherever you like.  You have two choices once you've created your
repository.  You can specify the path to the repository on the command line
using the '-R' flag.  Alternatively, you can create a configuration file at
'~/.dotfilesrc' and place the path to your repository in there.  The contents
would look like:

    [dotfiles]
    repository = ~/.my-dotfiles-repo

You can see more information by typing 'dotfiles -h'"""


def method_list(object):
    return [method for method in dir(object)
            if callable(getattr(object, method))]


def parse_args():
    parser = OptionParser(usage=USAGE)

    parser.set_defaults(config=os.path.expanduser("~/.dotfilesrc"))
    parser.set_defaults(ignore=[])
    parser.set_defaults(externals={})

    parser.add_option("-v", "--version", action="store_true",
            dest="show_version", default=False,
            help="show version number and exit")

    parser.add_option("-f", "--force", action="store_true", dest="force",
            default=False, help="ignore unmanaged dotfiles (use with --sync)")

    parser.add_option("-R", "--repo", type="string", dest="repo",
            help="set repository location (default is ~/Dotfiles)")

    parser.add_option("-p", "--prefix", type="string", dest="prefix",
            help="set prefix character (default is None)")

    parser.add_option("-C", "--config", type="string", dest="config",
            help="set configuration file location (default is ~/.dotfilesrc)")

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

    if opts.config:
        parser.read(opts.config)

        if 'dotfiles' in parser.sections():

            if not opts.repo:
                if parser.get('dotfiles', 'repository'):
                    opts.repo = os.path.expanduser(parser.get('dotfiles', 'repository'))
                else:
                    opts.repo = os.path.expanduser("~/Dotfiles")

            if not opts.prefix:
                if parser.get('dotfiles', 'prefix'):
                    opts.prefix = parser.get('dotfiles', 'prefix')
                else:
                    opts.prefix = ''

            if not opts.ignore and parser.get('dotfiles', 'ignore'):
                opts.ignore = eval(parser.get('dotfiles', 'ignore'))

            if not opts.externals and parser.get('dotfiles', 'externals'):
                opts.externals = eval(parser.get('dotfiles', 'externals'))

    if not os.path.exists(opts.repo):
        print "%s\n" % USAGE
        print NO_REPO_MESSAGE % opts.repo
        exit(-1)

    if not opts.action:
        print "%s\n" % USAGE
        print "Error: An action is required."
        exit(-1)

    getattr(core.Dotfiles(location=opts.repo,
                          prefix=opts.prefix,
                          ignore=opts.ignore,
                          externals=opts.externals,
                          force=opts.force), opts.action)(files=args)
