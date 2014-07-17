import os
from dotfiles.utils import compare_path as samefile


def _touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)


class HomeDirectory(object):


    def __init__(self, path, repo, contents):
        self.path = path
        self.repo = repo
        if contents:
            self.setup(contents)


    def setup(self, contents):
        repo = os.path.join(self.path, self.repo)
        os.mkdir(repo)

        for link, link_should_exist in contents.items():

            target = os.path.join('%s/%s' % (repo, link[1:]))
            _touch(target)

            if link_should_exist:
                os.symlink(target, os.path.join(self.path, link))

        self.verify(contents)


    def verify(self, contents):
        __tracebackhide__ = True

        for link, link_should_exist in contents.items():

            target = os.path.join(self.path, '%s/%s' % (self.repo, link[1:]))

            if not os.path.exists(target):
                pytest.fail("missing expected repo file \"%s\"" % target)

            link = os.path.join(self.path, link)
            link_exists = os.path.exists(link)

            if link_should_exist:
                if not link_exists:
                    pytest.fail("missing expected symlink \"%s\"" % link)
                if not samefile(link, target):
                    pytest.fail("\"%s\" does not link to \"%s\"" % (link, target))

            elif link_exists:
                pytest.fail("found unexpected symlink \"%s\"" % link)
