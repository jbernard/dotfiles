import pytest

from pathlib import Path
from dotfiles.repository import Repository, \
    REMOVE_LEADING_DOT, IGNORE_PATTERNS


def test_repo_create(repo):
    repo.path.rmdir()
    assert not repo.path.exists()

    Repository(repo.path, repo.homedir)
    assert repo.path.exists()
    assert repo.path.is_dir()


@pytest.mark.parametrize('dot', [REMOVE_LEADING_DOT, not REMOVE_LEADING_DOT])
@pytest.mark.parametrize('ignore', [IGNORE_PATTERNS, ['foo', 'bar', 'baz']])
def test_params(repo, dot, ignore):

    _repo = Repository(repo.path,
                       homedir=repo.homedir,
                       remove_leading_dot=dot,
                       ignore_patterns=ignore)

    assert _repo.path == repo.path
    assert _repo.homedir == repo.homedir
    assert _repo.remove_leading_dot == dot
    assert _repo.ignore_patterns == ignore


def test_contents(repo):
    assert repo.contents() == []

    target_a = repo.path / 'a'
    target_b = repo.path / 'b/b'
    target_c = repo.path / 'c/c/c'

    target_b.parent.mkdir()
    target_c.parent.mkdir(parents=True)

    target_a.touch()
    target_b.touch()
    target_c.touch()

    contents = repo.contents()

    assert contents[0].target == target_a
    assert contents[1].target == target_b
    assert contents[2].target == target_c


def test_str(repo):

    Path(repo.path / 'a').touch()
    Path(repo.path / 'b').touch()
    Path(repo.path / 'c').touch()

    assert str(repo) == (
        '%s\n%s\n%s' % (repo.homedir / '.a',
                        repo.homedir / '.b',
                        repo.homedir / '.c'))


@pytest.mark.parametrize('path', ['.foo', '.foo/bar/baz'])
def test_dotfile_path(repo, path):

    repo.remove_leading_dot = False
    assert (repo._dotfile_path(repo.path / path) ==
            repo.homedir / path)

    repo.remove_leading_dot = True
    assert (repo._dotfile_path(repo.path / path) ==
            repo.homedir / ('.%s' % path))


@pytest.mark.parametrize('path', ['.foo', '.foo/bar/baz'])
def test_dotfile_target(repo, path):

    repo.remove_leading_dot = False
    assert (repo._dotfile_target(repo.homedir / path) ==
            repo.path / path)

    repo.remove_leading_dot = True
    assert (repo._dotfile_target(repo.homedir / path) ==
            repo.path / path[1:])


# from dotfiles.exceptions import NotRootedInHome, InRepository, TargetIgnored,
#     IsDirectory


# def test_dotfile(repo):
#     with pytest.raises(NotRootedInHome):
#         repo._dotfile(py.path.local('/tmp/foo'))
#     with pytest.raises(TargetIgnored):
#         repo.ignore_patterns = ['.foo']
#         repo.remove_leading_dot = False
#         repo._dotfile(py.path.local(repo.homedir.join('.foo')))
#     with pytest.raises(TargetIgnored):
#         repo.ignore_patterns = ['foo']
#         repo._dotfile(repo.homedir.join('.bar/foo'))
#     with pytest.raises(IsDirectory):
#         repo._dotfile(repo.homedir.ensure_dir('.config'))

#     # The repo fixture is parametrized, we can only expect InRepository
#     # exception when the repository is contained in the home directory.
#     if repo.path.dirname == repo.homedir.basename:
#         with pytest.raises(InRepository):
#             repo._dotfile(repo.path.join('.foo/bar'))

#     repo._dotfile(repo.homedir.join('.foo'))


# def test_dotfiles(repo):
#     file = repo.homedir.join('.baz')
#     dir = repo.homedir.ensure_dir('.dir')
#     dir.ensure('foo/bat')
#     dir.ensure('foo/buz')
#     dir.ensure('bar')
#     dir.ensure('boo')

#     dotfiles = repo.dotfiles([str(file), str(dir)])
#     assert len(dotfiles) == 5


# def test_prune(repo):
#     repo.path.ensure_dir('.a/a')
#     repo.path.ensure_dir('.b/b/b/b')
#     repo.path.ensure_dir('.c/c/c/c/c/c/c/c')

#     repo.prune()
#     assert len(repo.path.listdir()) == 0
