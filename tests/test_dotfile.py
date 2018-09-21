import pytest
import py.path

from dotfiles.dotfile import Dotfile
from dotfiles.exceptions import \
    IsSymlink, NotASymlink, TargetExists, TargetMissing, Exists


def _dotfile(repo, name, target=None):
    return Dotfile(repo.homedir.join(name),
                   repo.path.join(target if target is not None else name))


@pytest.mark.parametrize('name', ['.a'])
def test_str(repo, name):
    dotfile = _dotfile(repo, name, '.b')
    assert str(dotfile) == repo.homedir.join(name)


@pytest.mark.parametrize('name', ['.foo'])
def test_short_name(repo, name):
    dotfile = _dotfile(repo, name)
    assert dotfile.name == repo.homedir.join(name)
    assert dotfile.short_name(repo.homedir) == name


def test_state(repo):
    dotfile = _dotfile(repo, '.vimrc', 'vimrc')
    assert dotfile.state == 'error'

    dotfile.target.ensure()
    dotfile.name.mksymlinkto(dotfile.target)
    assert dotfile.state == 'ok'

    dotfile.name.remove()
    assert dotfile.state == 'missing'

    dotfile.name.ensure()
    assert dotfile.state == 'ok'

    dotfile.name.write('test content')
    assert dotfile.state == 'conflict'

    dotfile.target.write('test content')
    assert dotfile.state == 'ok'


@pytest.mark.parametrize('path', ['.foo', '.foo/bar/baz'])
def test_add(repo, path):
    dotfile = _dotfile(repo, path)
    dotfile.target.ensure()
    dotfile.name.ensure()

    with pytest.raises(TargetExists):
        dotfile.add()

    dotfile.target.remove()
    dotfile.add()

    assert dotfile.target.check(file=1, link=0)
    assert dotfile.name.check(file=1, link=1)
    assert dotfile.name.samefile(dotfile.target)

    with pytest.raises(IsSymlink):
        dotfile.add()

    assert dotfile.target.check(file=1, link=0)
    assert dotfile.name.check(file=1, link=1)
    assert dotfile.name.samefile(dotfile.target)


@pytest.mark.parametrize('path', ['.foo', '.foo/bar/baz'])
def test_remove(repo, path):
    dotfile = _dotfile(repo, path)
    py.path.local(dotfile.name.dirname).ensure_dir()
    dotfile.name.mksymlinkto(dotfile.target)

    with pytest.raises(TargetMissing):
        dotfile.remove()

    dotfile.target.ensure()
    dotfile.remove()

    assert dotfile.target.check(exists=0)
    assert dotfile.name.check(file=1, link=0)

    with pytest.raises(NotASymlink):
        dotfile.remove()

    assert dotfile.target.check(exists=0)
    assert dotfile.name.check(file=1, link=0)


@pytest.mark.parametrize('path', ['.foo', '.foo/bar/baz'])
def test_link(repo, path):
    dotfile = _dotfile(repo, path)

    with pytest.raises(TargetMissing):
        dotfile.link()

    dotfile.target.ensure()
    dotfile.link()

    assert dotfile.target.check(file=1, link=0)
    assert dotfile.name.check(file=1, link=1)
    assert dotfile.name.samefile(dotfile.target)

    with pytest.raises(Exists):
        dotfile.link()

    assert dotfile.target.check(file=1, link=0)
    assert dotfile.name.check(file=1, link=1)
    assert dotfile.name.samefile(dotfile.target)


@pytest.mark.parametrize('path', ['.foo', '.foo/bar/baz'])
def test_unlink(repo, path):
    dotfile = _dotfile(repo, path)

    with pytest.raises(NotASymlink):
        dotfile.unlink()

    py.path.local(dotfile.name.dirname).ensure_dir()
    dotfile.name.mksymlinkto(dotfile.target)

    with pytest.raises(TargetMissing):
        dotfile.unlink()

    dotfile.target.ensure()
    dotfile.unlink()

    assert dotfile.target.check(file=1, link=0)
    assert dotfile.name.check(exists=0)

    with pytest.raises(NotASymlink):
        dotfile.unlink()

    assert dotfile.target.check(file=1, link=0)
    assert dotfile.name.check(exists=0)
