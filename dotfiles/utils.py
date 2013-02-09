"""
Misc utility functions.
"""

import os.path

from dotfiles.compat import islink, realpath


def compare_path(path1, path2):
    return (realpath_expanduser(path1) == realpath_expanduser(path2))


def realpath_expanduser(path):
    return realpath(os.path.expanduser(path))


def is_link_to(path, target):
    def normalize(path):
        return os.path.normcase(os.path.normpath(path))
    return islink(path) and \
        normalize(realpath(path)) == normalize(realpath(target))
