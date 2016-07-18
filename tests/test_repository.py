import pytest
import py.path

from dotfiles.repository import Repository
from dotfiles.exceptions import NotRootedInHome, InRepository, TargetIgnored, \
    IsDirectory


def test_repo_create(repo):
    repo.path.remove()
    assert repo.path.check(exists=0)
    Repository(repo.path, repo.homedir)
    assert repo.path.check(exists=1, dir=1)


def test_str(repo):
    repo.path.ensure('a')
    repo.path.ensure('b')
    repo.path.ensure('c')
    assert str(repo) == (
        '%s\n%s\n%s' % (repo.homedir.join('.a'),
                        repo.homedir.join('.b'),
                        repo.homedir.join('.c')))


@pytest.mark.parametrize('path', ['.foo', '.foo/bar/baz'])
def test_dotfile_path(repo, path):
    repo.remove_leading_dot = False
    assert (repo._dotfile_path(repo.path.join(path)) ==
            repo.homedir.join(path))
    repo.remove_leading_dot = True
    assert (repo._dotfile_path(repo.path.join(path)) ==
            repo.homedir.join('.%s' % path))


@pytest.mark.parametrize('path', ['.foo', '.foo/bar/baz'])
def test_dotfile_target(repo, path):
    repo.remove_leading_dot = False
    assert (repo._dotfile_target(repo.homedir.join(path)) ==
            repo.path.join(path))
    repo.remove_leading_dot = True
    assert (repo._dotfile_target(repo.homedir.join(path)) ==
            repo.path.join(path[1:]))


def test_dotfile(repo):
    with pytest.raises(NotRootedInHome):
        repo._dotfile(py.path.local('/tmp/foo'))
    with pytest.raises(TargetIgnored):
        repo.ignore_patterns = ['.foo']
        repo.remove_leading_dot = False
        repo._dotfile(py.path.local(repo.homedir.join('.foo')))
    with pytest.raises(TargetIgnored):
        repo.ignore_patterns = ['foo']
        repo._dotfile(repo.homedir.join('.bar/foo'))
    with pytest.raises(IsDirectory):
        repo._dotfile(repo.homedir.ensure_dir('.config'))

    # The repo fixture is parametrized, we can only expect InRepository
    # exception when the repository is contained in the home directory.
    if repo.path.dirname == repo.homedir.basename:
        with pytest.raises(InRepository):
            repo._dotfile(repo.path.join('.foo/bar'))

    repo._dotfile(repo.homedir.join('.foo'))


def test_dotfiles(repo):
    file = repo.homedir.join('.baz')
    dir = repo.homedir.ensure_dir('.dir')
    dir.ensure('foo/bat')
    dir.ensure('foo/buz')
    dir.ensure('bar')
    dir.ensure('boo')

    dotfiles = repo.dotfiles([str(file), str(dir)])
    assert len(dotfiles) == 5


def test_contents(repo):
    assert repo.contents() == []

    target_a = repo.path.ensure('a')
    target_b = repo.path.ensure('b/b')
    target_c = repo.path.ensure('c/c/c')
    contents = repo.contents()

    assert contents[0].target == target_a
    assert contents[1].target == target_b
    assert contents[2].target == target_c


def test_prune(repo):
    repo.path.ensure_dir('.a/a')
    repo.path.ensure_dir('.b/b/b/b')
    repo.path.ensure_dir('.c/c/c/c/c/c/c/c')

    repo.prune()
    assert len(repo.path.listdir()) == 0
