import pytest

from dotfiles import Repository, Dotfile, cli


class TestCli(object):

    def test_status(self, runner, repo, home, monkeypatch):

        def repo_init(self, *args, **kwargs):
            self.ignore = []
            self.homedir = home
            self.repodir = repo.ensure(dir=1)

        monkeypatch.setattr(Repository, '__init__', repo_init)

        result = runner.invoke(cli, ['status'])
        assert not result.exception
        assert result.output == ''


class TestRepository(object):

    def test_init(self, repo, home):
        repo.remove()
        assert repo.check(exists=0)

        r = Repository(repo, home)
        assert r.repodir == repo
        assert r.homedir == home
        assert repo.check(exists=1, dir=1)

    def test_str(self, repo, home):
        repo.ensure('a')
        repo.ensure('b')
        repo.ensure('c')
        assert str(Repository(repo, home)) == ('.a\n'
                                               '.b\n'
                                               '.c')

    def test_repr(self, repo):
        actual = '%r' % Repository(repo, None)
        expected = '<Repository local(\'%s\')>' % repo
        assert actual == expected

    def test_target_to_name(self, repo, home):
        actual = Repository(repo, home)._target_to_name(repo.join('foo'))
        expected = home.join('.foo')
        assert actual == expected

    def test_name_to_target(self, repo, home):
        actual = Repository(repo, home)._name_to_target(home.join('.foo'))
        expected = repo.join('foo')
        assert actual == expected

    @pytest.mark.xfail(reason='TODO')
    def test_dotifle(self):
        assert False

    def test_contents(self, repo, home):

        assert Repository(repo, home).contents() == []

        target_a = repo.ensure('a')
        target_b = repo.ensure('b')
        target_c = repo.ensure('c')
        contents = Repository(repo, home).contents()

        assert contents[0].target == target_a
        assert contents[1].target == target_b
        assert contents[2].target == target_c


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
                # TODO: verify exception type once those exists
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
