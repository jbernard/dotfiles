import py
import pytest

from dotfiles import Repository, Dotfile, cli


class TestCli(object):

    def test_status(self, runner, repo, home):
        result = runner.invoke(cli, ['--home-directory', str(home),
                                     '--repository', str(repo),
                                     'status'])
        assert not result.exception
        assert result.output == ''


class TestRepository(object):

    def test_repodir_create(self, repo, home):
        repo.remove()
        assert repo.check(exists=0)
        Repository(repo, home).contents()
        assert repo.check(exists=1, dir=1)

    def test_contents_empty(self, repo, home):
        assert Repository(repo, home).contents() == []

    def test_contents_nonempty(self, repo, home):
        target_a = repo.ensure('a')
        target_b = repo.ensure('b')
        target_c = repo.ensure('c')
        contents = Repository(repo, home).contents()

        assert contents[0].target == target_a
        assert contents[1].target == target_b
        assert contents[2].target == target_c

    def test_expected_name(self, repo, home):
        actual = Repository(repo, home).expected_name(repo.join('foo'))
        expected = home.join('.foo')
        assert actual == expected


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
            with pytest.raises(OSError):
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
            with pytest.raises(OSError):
                Dotfile(name, target).remove()
            assert not target.check()
            assert name.check(file=1, link=0)

    @pytest.mark.parametrize('times', range(1, 4))
    def test_sync(self, repo, home, times):
        name = home.join('.vimrc')
        target = repo.ensure('vimrc')

        Dotfile(name, target).sync()

        assert target.check(file=1, link=0)
        assert name.check(file=1, link=1)
        assert name.samefile(target)

        for x in range(2, times):
            with pytest.raises(py.error.EEXIST):
                Dotfile(name, target).sync()
            assert target.check(file=1, link=0)
            assert name.check(file=1, link=1)
            assert name.samefile(target)

    @pytest.mark.xfail(reason='not implemented yet')
    def test_unsync(self):
        assert False
