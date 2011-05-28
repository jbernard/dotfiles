# -*- coding: utf-8 -*-

import os
from . import core
import ConfigParser
from optparse import OptionParser, OptionGroup


def method_list(object):
    return [method for method in dir(object)
            if callable(getattr(object, method))]


def parse_args():
    parser = OptionParser(usage="Usage: %prog ACTION [OPTION...] [FILE...]")

    parser.set_defaults(config=os.path.expanduser("~/.dotfilesrc"))
    parser.set_defaults(repo=os.path.expanduser("~/Dotfiles"))
    parser.set_defaults(prefix='')
    parser.set_defaults(ignore=[])
    parser.set_defaults(externals={})

    parser.add_option("-C", "--config", type="string", dest="config",
            help="set configuration file location (default is ~/.dotfilesrc)")

    parser.add_option("-R", "--repo", type="string", dest="repo",
            help="set repository location (default is ~/Dotfiles)")

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

    if not os.path.exists(opts.repo):
        parser.error("Could not find dotfiles repository \"%s\"" % opts.repo)

    if not opts.action:
        parser.error("An action is required.")

    if opts.action not in method_list(core.Dotfiles):
        parser.error("No such action \"%s\"" % opts.action)

    return (opts, args)


def main():

    (opts, args) = parse_args()

    config_defaults = {
            'repository':   opts.repo,
            'prefix':       opts.prefix,
            'ignore':       opts.ignore,
            'externals':    opts.externals}

    parser = ConfigParser.SafeConfigParser(config_defaults)

    if opts.config:

        parser.read(opts.config)

        if 'dotfiles' in parser.sections():
            opts.repo = os.path.expanduser(parser.get('dotfiles', 'repository'))
            opts.prefix = parser.get('dotfiles', 'prefix')
            opts.ignore = eval(parser.get('dotfiles', 'ignore'))
            opts.externals = eval(parser.get('dotfiles', 'externals'))

    getattr(core.Dotfiles(location=opts.repo,
                          prefix=opts.prefix,
                          ignore=opts.ignore,
                          externals=opts.externals), opts.action)(files=args)
