import py
import pytest
from click.testing import CliRunner

from dotfiles import __version__
from dotfiles import Repository
from dotfiles import Dotfile, unique_suffix
from dotfiles import version


class TestCLI(object):

    def test_version(self):
        runner = CliRunner()
        result = runner.invoke(version)
        assert ('dotfiles version %s\n' % __version__) == result.output

    """
    @pytest.mark.xfail()
    def test_empty_status(tmpdir):
        repo = Repository(tmpdir.join("repo"))
        assert '[no dotfiles found]' == repo.status()

    @pytest.mark.xfail()
    def test_status_manual(tmpdir, monkeypatch):

        repodir = tmpdir.join("Dotfiles", dir=1)
        target = repodir.ensure("vimrc")
        name = tmpdir.ensure(".vimrc")

        dotfile = Dotfile(name, target)

        repo = Repository(repodir, tmpdir)
        monkeypatch.setattr(Repository, "_load",
                            lambda self: [dotfile, dotfile, dotfile])

        dotfile_state = 'conflict'
        expected_status = ("{0:<18} {1}\n"
                           "{0:<18} {1}\n"
                           "{0:<18} {1}".format(name.basename, dotfile_state))

        assert expected_status == repo.status()

    @pytest.mark.xfail()
    def test_status_discover(tmpdir):

        repodir = tmpdir.ensure("Dotfiles", dir=1)

        tmpdir.join('.bashrc').mksymlinkto(repodir.ensure('bashrc'))
        tmpdir.join('.inputrc').mksymlinkto(repodir.ensure('inputrc'))
        tmpdir.join('.vimrc').mksymlinkto(repodir.ensure('vimrc'))

        repo = Repository(repodir, tmpdir)

        expected_status = ("{1:<18} {0}\n"
                           "{2:<18} {0}\n"
                           "{3:<18} {0}".format('ok',
                                                '.bashrc',
                                                '.inputrc',
                                                '.vimrc'))

        assert expected_status == repo.status()

    @pytest.mark.xfail()
    def test_check(tmpdir, monkeypatch):

        repodir = tmpdir.join('repo')

        dotfile_a = Dotfile(tmpdir.join('.aaa'), repodir.join('aaa'))
        dotfile_b = Dotfile(tmpdir.join('.bbb'), repodir.join('bbb'))
        dotfile_c = Dotfile(tmpdir.join('.ccc'), repodir.join('ccc'))

        dotfile_b.state = 'ok'

        repo = Repository(tmpdir)
        monkeypatch.setattr(Repository, "_load",
                            lambda self: [dotfile_a, dotfile_b, dotfile_c])

        expected_status = ("{1:<18} {0}\n"
                           "{2:<18} {0}".format('error',
                                                dotfile_a.name.basename,
                                                dotfile_c.name.basename))

        assert expected_status == repo.check()
        """


class TestRepository(object):

    def test_repodir_create(self, tmpdir):
        repodir = tmpdir.join('test_create_repo')
        repo = Repository(repodir, tmpdir)

        assert True == repodir.check(exists=0)
        repo.contents()
        assert True == repodir.check(exists=1, dir=1)

    def test_contents_empty(self, tmpdir):
        assert [] == Repository(tmpdir.join('Dotfiles'), tmpdir).contents()

    def test_contents_nonempty(self, tmpdir):
        repodir = tmpdir.ensure('test_create_repo', dir=1)
        target_a = repodir.ensure('a')
        target_b = repodir.ensure('b')
        target_c = repodir.ensure('c')

        contents = Repository(repodir, tmpdir).contents()

        assert target_a == contents[0].target
        assert target_b == contents[1].target
        assert target_c == contents[2].target

    @pytest.mark.xfail(reason='not implemented yet')
    def test_expected_name(self):
        assert 0


class TestDotfile(object):

    def test_unique_suffix_overlap(self):
        (name, target) = unique_suffix(py.path.local('/foo/baz'),
                                       py.path.local('/foo/bar/bat'))
        assert 'baz' == name
        assert 'bar/bat' == target

    @pytest.mark.xfail(reason='this is a bug')
    def test_unique_suffix_no_overlap(self):
        (name, target) = unique_suffix(py.path.local('/a/b/c'),
                                       py.path.local('/d/e/f'))
        assert '/a/b/c' == name
        assert '/d/e/f' == target

    def test_state_error(self, tmpdir):
        repo = tmpdir.ensure("Dotfiles", dir=1)
        name = tmpdir.join(".vimrc")
        target = repo.join("vimrc")

        dotfile = Dotfile(name, target)

        assert 'error' == dotfile.state

    def test_state_missing(self, tmpdir):
        repo = tmpdir.ensure("Dotfiles", dir=1)
        name = tmpdir.join(".vimrc")
        target = repo.ensure("vimrc")

        dotfile = Dotfile(name, target)

        assert 'missing' == dotfile.state

    def test_state_conflict(self, tmpdir):
        repo = tmpdir.ensure("Dotfiles", dir=1)
        name = tmpdir.ensure(".vimrc")
        target = repo.ensure("vimrc")

        dotfile = Dotfile(name, target)

        assert 'conflict' == dotfile.state

    def test_state_ok(self, tmpdir):
        repo = tmpdir.join("Dotfiles", dir=1)
        name = tmpdir.join(".vimrc")
        target = repo.ensure("vimrc")
        dotfile = Dotfile(name, target)

        name.mksymlinkto(target)
        assert 'ok' == dotfile.state

        name.remove()
        assert 'missing' == dotfile.state

    @pytest.mark.parametrize("times", range(1, 4))
    def test_add(self, tmpdir, times):
        repo = tmpdir.ensure("Dotfiles", dir=1)
        name = tmpdir.ensure(".vimrc")
        target = repo.join("vimrc")

        dotfile = Dotfile(name, target)
        dotfile.add()

        assert target.check(file=1, link=0)
        assert name.check(file=1, link=1)
        assert name.samefile(target)

        for x in range(2, times):
            with pytest.raises(OSError):
                dotfile.add()
            assert target.check(file=1, link=0)
            assert name.check(file=1, link=1)
            assert name.samefile(target)

    @pytest.mark.parametrize("times", range(1, 4))
    def test_remove(self, tmpdir, times):
        repo = tmpdir.ensure("Dotfiles", dir=1)
        name = tmpdir.join(".vimrc")
        target = repo.ensure("vimrc")

        name.mksymlinkto(target)

        dotfile = Dotfile(name, target)
        dotfile.remove()

        assert False == target.check()
        assert name.check(file=1, link=0)

        for x in range(2, times):
            with pytest.raises(OSError):
                dotfile.remove()
            assert False == target.check()
            assert name.check(file=1, link=0)

    @pytest.mark.parametrize("times", range(1, 4))
    def test_sync(self, tmpdir, times):
        repo = tmpdir.ensure("Dotfiles", dir=1)
        name = tmpdir.join(".vimrc")
        target = repo.ensure("vimrc")

        dotfile = Dotfile(name, target)
        dotfile.sync()

        assert target.check(file=1, link=0)
        assert name.check(file=1, link=1)
        assert name.samefile(target)

        for x in range(2, times):
            with pytest.raises(py.error.EEXIST):
                dotfile.sync()
            assert target.check(file=1, link=0)
            assert name.check(file=1, link=1)
            assert name.samefile(target)

    @pytest.mark.xfail(reason='not implemented yet')
    def test_unsync(self):
        assert 0
