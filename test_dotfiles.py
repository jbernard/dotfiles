import py
import pytest

from dotfiles import cli, unique_suffix
from dotfiles import Repository, Dotfile


def test_unique_suffix_overlap():
    (name, target) = unique_suffix(py.path.local('/foo/baz'),
                                   py.path.local('/foo/bar/bat'))
    assert name == 'baz'
    assert target == 'bar/bat'


@pytest.mark.xfail(reason='this is a bug')
def test_unique_suffix_no_overlap():
    (name, target) = unique_suffix(py.path.local('/a/b/c'),
                                   py.path.local('/d/e/f'))
    assert name == '/a/b/c'
    assert target == '/d/e/f'


class TestCli(object):

    def test_list_empty(self, runner, repo, home):
        result = runner.invoke(cli, ['--home-directory', str(home),
                                     '--repository', str(repo),
                                     'list'])
        assert not result.exception
        assert result.output == '[no dotfiles found]\n'

    def test_list(self, runner, repo, home):
        repo.ensure('foo')
        repo.ensure('bar')
        repo.ensure('baz')
        result = runner.invoke(cli, ['--home-directory', str(home),
                                     '--repository', str(repo),
                                     'list'])
        assert not result.exception
        assert result.output == ('.bar\n'
                                 '.baz\n'
                                 '.foo\n')

    def test_list_verbose(self, runner, repo, home):
        repo.ensure('baz')
        repo.ensure('foo')
        home.ensure('.foo')
        home.join('.bar').mksymlinkto(repo.ensure('bar'))

        result = runner.invoke(cli, ['--home-directory', str(home),
                                     '--repository', str(repo),
                                     'list', '--verbose'])
        assert not result.exception
        assert result.output == (
            '.bar               (ok)\n'
            '.baz               (missing)\n'
            '.foo               (conflict)\n')

    def test_staus(self):
        pass


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

    @pytest.mark.xfail(reason='not implemented yet')
    def test_expected_name(self):
        assert False


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
