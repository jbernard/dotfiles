import pytest

from pathlib import Path
from dotfiles.exceptions import NotRootedInHome, TargetIgnored, \
    IsDirectory, InRepository
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


def test_dotfile(repo):

    with pytest.raises(NotRootedInHome):
        repo._dotfile(Path('/tmp/foo'))

    with pytest.raises(TargetIgnored):
        repo.ignore_patterns = ['.foo']
        repo.remove_leading_dot = False
        repo._dotfile(repo.homedir / '.foo')

    with pytest.raises(TargetIgnored):
        repo.ignore_patterns = ['foo']
        repo._dotfile(repo.homedir / '.bar/foo')

    with pytest.raises(IsDirectory):
        dir = repo.homedir / '.config'
        dir.mkdir()
        repo._dotfile(dir)

    # The repo fixture is parametrized, we can only expect InRepository
    # exception when the repository is contained in the home directory.
    if repo.path.parent == repo.homedir.name:
        with pytest.raises(InRepository):
            repo._dotfile(repo.path / '.foo/bar')


def test_dotfiles(repo):

    subdir_a = repo.homedir / '.dir'
    subdir_b = repo.homedir / '.dir/foo'

    for subdir in [subdir_a, subdir_b]:
        subdir.mkdir()

    file_a = repo.homedir / '.baz'
    file_b = subdir_a / 'bar'
    file_c = subdir_a / 'boo'
    file_d = subdir_b / 'bat'
    file_e = subdir_b / 'buz'

    for file in [file_a, file_b, file_c, file_d, file_e]:
        file.touch()

    dotfiles = repo.dotfiles([str(file_a), str(subdir_a)])

    assert len(dotfiles) == 5

    for file in [file_a, file_b, file_c, file_d, file_e]:
        assert str(file) in map(str, dotfiles)


def test_prune(repo):
    dir_a = repo.path / '.a/a'
    dir_b = repo.path / '.b/b/b/b'
    dir_c = repo.path / '.c/c/c/c/c/c/c/c'

    for dir in [dir_a, dir_b, dir_c]:
        dir.mkdir(parents=True)

    repo.prune()
    contents = [x for x in repo.path.rglob('*')]
    assert len(contents) == 0

    # verify ignored directories are excluded from pruning
    dir_d = repo.path / '.git'
    dir_d.mkdir()

    repo.prune()
    contents = [x for x in repo.path.rglob('*')]
    assert str(dir_d) in map(str, contents)
    assert len(contents) == 1
