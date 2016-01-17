import pytest

from dotfiles.dotfile import Dotfile
from dotfiles.exceptions import IsSymlink


class TestDotfile(object):

    def test_state_error(self, repo, home):
        dotfile = Dotfile(home.join('.vimrc'), repo.join('vimrc'))
        assert dotfile.state == 'error'

    def test_state_missing(self, repo, home):
        dotfile = Dotfile(home.join('.vimrc'), repo.ensure('vimrc'))
        assert dotfile.state == 'missing'

    def test_state_conflict(self, repo, home):
        dotfile = Dotfile(home.ensure('.vimrc'), repo.ensure('vimrc'))
        assert dotfile.state == 'conflict'

    def test_state_ok(self, repo, home):
        name = home.join('.vimrc')
        target = repo.ensure('vimrc')

        dotfile = Dotfile(name, target)
        name.mksymlinkto(target)
        assert dotfile.state == 'ok'

        name.remove()
        assert dotfile.state == 'missing'

    @pytest.mark.parametrize('times', range(1, 4))
    def test_add(self, repo, home, times):
        name = home.ensure('.vimrc')
        target = repo.join('vimrc')

        Dotfile(name, target).add()

        assert target.check(file=1, link=0)
        assert name.check(file=1, link=1)
        assert name.samefile(target)

        for x in range(2, times):
            with pytest.raises(IsSymlink):
                Dotfile(name, target).add()
            assert target.check(file=1, link=0)
            assert name.check(file=1, link=1)
            assert name.samefile(target)

    @pytest.mark.parametrize('times', range(1, 4))
    def test_remove(self, repo, home, times):
        name = home.join('.vimrc')
        target = repo.ensure('vimrc')

        name.mksymlinkto(target)
        Dotfile(name, target).remove()

        assert not target.check()
        assert name.check(file=1, link=0)

        for x in range(2, times):
            with pytest.raises(Exception):
                # TODO: verify exception type once those exists
                Dotfile(name, target).remove()
            assert not target.check()
            assert name.check(file=1, link=0)

    @pytest.mark.parametrize('times', range(1, 4))
    def test_link(self, repo, home, times):
        name = home.join('.vimrc')
        target = repo.ensure('vimrc')

        Dotfile(name, target).link()

        assert target.check(file=1, link=0)
        assert name.check(file=1, link=1)
        assert name.samefile(target)

        for x in range(2, times):
            with pytest.raises(Exception):
                # TODO: verify exception type once those exists
                Dotfile(name, target).link()
            assert target.check(file=1, link=0)
            assert name.check(file=1, link=1)
            assert name.samefile(target)

    @pytest.mark.xfail(reason='TODO')
    def test_unlink(self):
        assert False
