import py
import pytest

from dotfiles.repository import Repository
from dotfiles.exceptions import NotRootedInHome, InRepository, TargetIgnored, \
    IsDirectory


def test_repo_create(repo, home):
    repo.remove()
    assert repo.check(exists=0)
    Repository(repo, home)
    assert repo.check(exists=1, dir=1)


def test_str(repo, home):
    repo.ensure('.a')
    repo.ensure('.b')
    repo.ensure('.c')

    r = Repository(repo, home)

    assert str(r) == (
        '%s\n%s\n%s' % (home.join('.a'),
                        home.join('.b'),
                        home.join('.c')))


@pytest.mark.parametrize('path', ['.foo', '.foo/bar/baz'])
def test_target_to_name(repo, home, path):
    r = Repository(repo, home, dot=True)
    assert r._target_to_name(repo.join(path)) == home.join(path)

    r = Repository(repo, home, dot=False)
    assert r._target_to_name(repo.join(path)) == home.join('.%s' % path)


@pytest.mark.parametrize('path', ['.foo', '.foo/bar/baz'])
def test_name_to_target(repo, home, path):
    r = Repository(repo, home, dot=True)
    assert r._name_to_target(home.join(path)) == repo.join(path)

    r = Repository(repo, home, dot=False)
    assert r._name_to_target(home.join(path)) == repo.join(path[1:])


def test_dotfile(repo, home):
    with pytest.raises(NotRootedInHome):
        Repository(repo, home)._dotfile(py.path.local('/tmp/foo'))
    with pytest.raises(TargetIgnored):
        Repository(repo, home, ignore=['.foo'])._dotfile(home.join('.foo'))
    with pytest.raises(TargetIgnored):
        Repository(repo, home, ignore=['foo'])._dotfile(home.join('.bar/foo'))
    with pytest.raises(IsDirectory):
        Repository(repo, home)._dotfile(home.ensure_dir('.config'))

    # The home fixture is parametrized, we can only expect InRepository
    # exception when the repository is contained in the home directory.
    if repo.dirname == home.basename:
        with pytest.raises(InRepository):
            Repository(repo, home)._dotfile(repo.join('.foo/bar'))

    Repository(repo, home)._dotfile(home.join('.foo'))


def test_dotfiles(repo, home):
    file = home.join('.baz')
    dir = home.ensure_dir('.dir')
    dir.ensure('foo/bat')
    dir.ensure('foo/buz')
    dir.ensure('bar')
    dir.ensure('boo')

    dotfiles = Repository(repo, home).dotfiles([str(file), str(dir)])
    assert len(dotfiles) == 5


def test_contents(repo, home):
    assert Repository(repo, home).contents() == []

    target_a = repo.ensure('a')
    target_b = repo.ensure('b/b')
    target_c = repo.ensure('c/c/c')
    contents = Repository(repo, home).contents()

    assert contents[0].target == target_a
    assert contents[1].target == target_b
    assert contents[2].target == target_c


# TODO: Need tests for whatever-dot option


def test_prune(repo, home):
    repo.ensure_dir('.a/a')
    repo.ensure_dir('.b/b/b/b')
    repo.ensure_dir('.c/c/c/c/c/c/c/c')

    Repository(repo, home).prune()

    assert len(repo.listdir()) == 0
