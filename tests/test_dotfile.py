import pytest
import py.error

from dotfiles.dotfile import Dotfile


@pytest.mark.parametrize("times", range(1, 4))
def test_add(tmpdir, times):

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
def test_remove(tmpdir, times):

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
def test_sync(tmpdir, times):

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


def test_state_error(tmpdir):

    repo = tmpdir.ensure("Dotfiles", dir=1)
    name = tmpdir.join(".vimrc")
    target = repo.join("vimrc")

    dotfile = Dotfile(name, target)

    assert Dotfile.states['error'] == dotfile.state


def test_state_missing(tmpdir):

    repo = tmpdir.ensure("Dotfiles", dir=1)
    name = tmpdir.join(".vimrc")
    target = repo.ensure("vimrc")

    dotfile = Dotfile(name, target)

    assert Dotfile.states['missing'] == dotfile.state


def test_state_conflict(tmpdir):

    repo = tmpdir.ensure("Dotfiles", dir=1)
    name = tmpdir.ensure(".vimrc")
    target = repo.ensure("vimrc")

    dotfile = Dotfile(name, target)

    assert Dotfile.states['conflict'] == dotfile.state


def test_state_ok(tmpdir):

    repo = tmpdir.join("Dotfiles", dir=1)
    name = tmpdir.join(".vimrc")
    target = repo.ensure("vimrc")

    name.mksymlinkto(target)

    dotfile = Dotfile(name, target)

    assert Dotfile.states['ok'] == dotfile.state


def test_is_ok(tmpdir):

    repo = tmpdir.join("Dotfiles", dir=1)
    name = tmpdir.join(".vimrc")
    target = repo.ensure("vimrc")
    name.mksymlinkto(target)

    dotfile = Dotfile(name, target)

    assert Dotfile.states['ok'] == dotfile.state
    assert True == dotfile.is_ok()

    dotfile.state = Dotfile.states['conflict']
    assert False == dotfile.is_ok()
