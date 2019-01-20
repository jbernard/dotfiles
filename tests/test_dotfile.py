import pytest

from pathlib import Path
from dotfiles.dotfile import Dotfile
from dotfiles.pathutils import is_file, is_link, touch, mkdir
from dotfiles.exceptions import TargetExists, IsSymlink, \
    TargetMissing, NotASymlink, Exists


def _make_dotfile(repo, name, target=None):
    return Dotfile(repo.homedir.joinpath(name),
                   repo.path.joinpath(target if target else name))


@pytest.mark.parametrize('name', ['.a'])
def test_str(repo, name):
    dotfile = _make_dotfile(repo, name, '.b')
    assert dotfile.name == repo.homedir / name


@pytest.mark.parametrize('name', ['.foo'])
def test_short_name(repo, name):
    dotfile = _make_dotfile(repo, name)
    assert dotfile.name == repo.homedir / name
    assert dotfile.short_name(repo.homedir) == Path(name)


def test_is_present(repo):
    dotfile = _make_dotfile(repo, '.foo')
    assert not dotfile.is_present()
    # TODO: more


def test_state(repo):
    dotfile = _make_dotfile(repo, '.vimrc', 'vimrc')
    assert dotfile.state == 'error'

    dotfile.target.touch()
    dotfile.name.symlink_to(dotfile.target)
    assert dotfile.state == 'ok'

    dotfile.name.unlink()
    assert dotfile.state == 'missing'

    dotfile.name.touch()
    assert dotfile.state == 'ok'

    dotfile.name.write_text('test content')
    assert dotfile.state == 'conflict'

    dotfile.target.write_text('test content')
    assert dotfile.state == 'ok'


@pytest.mark.parametrize('path', ['.foo', '.foo/bar/baz'])
def test_add(repo, path):
    dotfile = _make_dotfile(repo, path)

    touch(dotfile.name)
    touch(dotfile.target)

    with pytest.raises(TargetExists):
        dotfile.add()
    dotfile.target.unlink()

    dotfile.add()
    assert is_link(dotfile.name)
    assert is_file(dotfile.target)
    assert dotfile.name.samefile(dotfile.target)

    with pytest.raises(IsSymlink):
        dotfile.add()
    assert is_file(dotfile.target)
    assert dotfile.name.samefile(dotfile.target)


@pytest.mark.parametrize('path', ['.foo', '.foo/bar/baz'])
def test_remove(repo, path):
    dotfile = _make_dotfile(repo, path)

    # py.path.local(dotfile.name.dirname).ensure_dir()
    # dotfile.name.mksymlinkto(dotfile.target)
    # dotfile.name.parent.mkdir(parents=True)
    mkdir(dotfile.name.parent)
    dotfile.name.symlink_to(dotfile.target)

    with pytest.raises(TargetMissing):
        dotfile.remove()

    # dotfile.target.ensure()
    # dotfile.target.touch()
    touch(dotfile.target)
    dotfile.remove()

    # assert dotfile.target.check(exists=0)
    # assert dotfile.name.check(file=1, link=0)
    assert not dotfile.target.exists()
    assert is_file(dotfile.name)

    with pytest.raises(NotASymlink):
        dotfile.remove()

    # assert dotfile.target.check(exists=0)
    # assert dotfile.name.check(file=1, link=0)
    assert not dotfile.target.exists()
    assert is_file(dotfile.name)


@pytest.mark.parametrize('path', ['.foo', '.foo/bar/baz'])
def test_link(repo, path):
    dotfile = _make_dotfile(repo, path)

    with pytest.raises(TargetMissing):
        dotfile.link()

    touch(dotfile.target)
    dotfile.link()

    assert is_file(dotfile.target)
    assert is_link(dotfile.name)
    assert dotfile.name.samefile(dotfile.target)

    with pytest.raises(Exists):
        dotfile.link()

    assert is_file(dotfile.target)
    assert is_link(dotfile.name)
    assert dotfile.name.samefile(dotfile.target)


@pytest.mark.parametrize('path', ['.foo', '.foo/bar/baz'])
def test_unlink(repo, path):
    dotfile = _make_dotfile(repo, path)

    with pytest.raises(NotASymlink):
        dotfile.unlink()

    # py.path.local(dotfile.name.dirname).ensure_dir()
    # dotfile.name.mksymlinkto(dotfile.target)
    mkdir(dotfile.name.parent)
    dotfile.name.symlink_to(dotfile.target)

    with pytest.raises(TargetMissing):
        dotfile.unlink()

    # dotfile.target.ensure()
    touch(dotfile.target)
    dotfile.unlink()

    assert is_file(dotfile.target)
    assert not dotfile.name.exists()

    with pytest.raises(NotASymlink):
        dotfile.unlink()

    assert is_file(dotfile.target)
    assert not dotfile.name.exists()


@pytest.mark.parametrize('path', ['.foo', '.foo/bar/baz'])
def test_copy(repo, path):
    pass
    # dotfile = _make_dotfile(repo, path)
    # TODO
