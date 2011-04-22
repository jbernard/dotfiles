# -*- coding: utf-8 -*-

import os
from . import core
from optparse import OptionParser, OptionGroup


def method_list(object):
    return [method for method in dir(object)
            if callable(getattr(object, method))]


def parse_args():
    parser = OptionParser(usage="Usage: %prog ACTION [OPTION...] [FILE...]")

    parser.set_defaults(repo=os.path.expanduser("~/Dotfiles"))
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
    getattr(core.Dotfiles(location=opts.repo), opts.action)(files=args)
