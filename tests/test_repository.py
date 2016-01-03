import os
import py
import pytest

from dotfiles.repository import Repository


def test_getters():

    repo = Repository('/a', '/b')

    assert isinstance(repo.homedir, str)
    assert isinstance(repo.repodir, str)

    assert '/a' == repo.repodir
    assert '/b' == repo.homedir


def test_setters():

    repodir = py.path.local('/foo/bar')
    homedir = py.path.local('/fizz/buzz')

    repo = Repository('/a', '/b')

    repo.repodir = repodir
    repo.homedir = homedir

    assert repodir == repo.repodir
    assert homedir == repo.homedir


def test_path_expansion():

    repo = Repository('~/foo', '~/bar')

    assert os.path.expanduser('~/foo') == repo.repodir
    assert os.path.expanduser('~/bar') == repo.homedir


def test_repodir_create(tmpdir):

    repodir = tmpdir.join('test_create_repo')
    repo = Repository(repodir)

    assert True == repodir.check(exists=0)
    contents = repo.contents()
    assert [] == contents
    assert True == repodir.check(exists=1, dir=1)


def test_contents_empty(tmpdir):
    assert [] == Repository(tmpdir.join('Dotfiles')).contents()


def test_contents_nonempty(tmpdir):

    repodir = tmpdir.ensure('test_create_repo', dir=1)
    target_a = repodir.ensure('a')
    target_b = repodir.ensure('b')
    target_c = repodir.ensure('c')

    contents = Repository(repodir).contents()

    assert target_a == contents[0].target
    assert target_b == contents[1].target
    assert target_c == contents[2].target


@pytest.mark.xfail(reason='not implemented yet')
def test_rename():
    raise NotImplementedError
