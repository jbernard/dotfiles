import py
import pytest

from dotfiles.dotfile import Dotfile
from dotfiles.exceptions import IsSymlink, NotASymlink
from dotfiles.exceptions import TargetExists, TargetMissing, Exists


def test_str(repo, home):
    dotfile = Dotfile(home.join('.a'), repo.join('.b'))
    assert str(dotfile) == home.join('.a')


def test_short_name(repo, home):
    dotfile = Dotfile(home.join('.foo'), repo.join('.foo'))
    assert dotfile.name == home.join('.foo')
    assert dotfile.short_name(home) == '.foo'


def test_state_error(repo, home):
    dotfile = Dotfile(home.join('.vimrc'), repo.join('.vimrc'))
    assert dotfile.state == 'error'


def test_state_missing(repo, home):
    dotfile = Dotfile(home.join('.vimrc'), repo.ensure('.vimrc'))
    assert dotfile.state == 'missing'


def test_state_conflict(repo, home):
    dotfile = Dotfile(home.ensure('.vimrc'), repo.ensure('.vimrc'))
    assert dotfile.state == 'conflict'


def test_state_ok(repo, home):
    name = home.join('.vimrc')
    target = repo.ensure('vimrc')

    dotfile = Dotfile(name, target)
    name.mksymlinkto(target)
    assert dotfile.state == 'ok'

    name.remove()
    assert dotfile.state == 'missing'


@pytest.mark.parametrize('path', ['.foo', '.foo/bar/baz'])
def test_add(repo, home, path):
    name = home.ensure(path)
    target = repo.ensure(path)
    dotfile = Dotfile(name, target)

    with pytest.raises(TargetExists):
        dotfile.add()

    target.remove()
    dotfile.add()

    assert target.check(file=1, link=0)
    assert name.check(file=1, link=1)
    assert name.samefile(target)

    with pytest.raises(IsSymlink):
        dotfile.add()

    assert target.check(file=1, link=0)
    assert name.check(file=1, link=1)
    assert name.samefile(target)


@pytest.mark.parametrize('path', ['.foo', '.foo/bar/baz'])
def test_remove(repo, home, path):
    name = home.join(path)
    target = repo.join(path)
    dotfile = Dotfile(name, target)

    py.path.local(name.dirname).ensure_dir()
    name.mksymlinkto(target)

    with pytest.raises(TargetMissing):
        dotfile.remove()

    target.ensure()
    dotfile.remove()

    assert target.check(exists=0)
    assert name.check(file=1, link=0)

    with pytest.raises(NotASymlink):
        dotfile.remove()

    assert target.check(exists=0)
    assert name.check(file=1, link=0)


@pytest.mark.parametrize('path', ['.foo', '.foo/bar/baz'])
def test_link(repo, home, path):
    name = home.join(path)
    target = repo.join(path)
    dotfile = Dotfile(name, target)

    with pytest.raises(TargetMissing):
        dotfile.link()

    target.ensure()
    dotfile.link()

    assert target.check(file=1, link=0)
    assert name.check(file=1, link=1)
    assert name.samefile(target)

    with pytest.raises(Exists):
        dotfile.link()

    assert target.check(file=1, link=0)
    assert name.check(file=1, link=1)
    assert name.samefile(target)


@pytest.mark.parametrize('path', ['.foo', '.foo/bar/baz'])
def test_unlink(repo, home, path):
    name = home.join(path)
    target = repo.join(path)
    dotfile = Dotfile(name, target)

    with pytest.raises(NotASymlink):
        dotfile.unlink()

    py.path.local(name.dirname).ensure_dir()
    name.mksymlinkto(target)

    with pytest.raises(TargetMissing):
        dotfile.unlink()

    target.ensure()
    dotfile.unlink()

    assert target.check(file=1, link=0)
    assert name.check(exists=0)

    with pytest.raises(NotASymlink):
        dotfile.unlink()

    assert target.check(file=1, link=0)
    assert name.check(exists=0)
