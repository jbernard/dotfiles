import os
import pytest

from dotfiles.dotfile import Dotfile
from dotfiles.repository import Repository


def test_getters():

    repo = Repository('foo', 'bar')

    assert isinstance(repo.homedir, str)
    assert isinstance(repo.repodir, str)


def test_setters():

    repodir = '/foo/bar'
    homedir = '/fizz/buzz'

    repo = Repository('foo', 'bar')

    repo.repodir = repodir
    repo.homedir = homedir

    assert repodir == repo.repodir
    assert homedir == repo.homedir


def test_custom_paths():

    homedir = '/foo/bar'
    repodir = '/fizz/buzz'

    repo = Repository(repodir, homedir)

    assert homedir == repo.homedir
    assert repodir == repo.repodir


def test_path_expansion():

    repo = Repository('~/foo', '~/bar')

    assert os.path.expanduser('~/foo') == repo.repodir
    assert os.path.expanduser('~/bar') == repo.homedir


def test_create_repo(tmpdir):

    repodir = tmpdir.join("test_create_repo")

    repodir.check(exists=0)
    Repository(repodir)
    repodir.check(exists=1, dir=1)


def test_empty_status(tmpdir):

    repo = Repository(tmpdir.join("repo"))

    assert '[no dotfiles found]' == repo.status()


def test_status_manual(tmpdir, monkeypatch):

    repodir = tmpdir.join("Dotfiles", dir=1)
    target = repodir.ensure("vimrc")
    name = tmpdir.ensure(".vimrc")

    dotfile = Dotfile(name, target)

    repo = Repository(repodir, tmpdir)
    monkeypatch.setattr(Repository, "_load",
                        lambda self: [dotfile, dotfile, dotfile])

    dotfile_state = Dotfile.states['conflict']['text']
    expected_status = ("{0:<18} {1}\n"
                       "{0:<18} {1}\n"
                       "{0:<18} {1}".format(name.basename, dotfile_state))

    assert expected_status == repo.status()


def test_status_discover(tmpdir):

    repodir = tmpdir.ensure("Dotfiles", dir=1)

    tmpdir.join('.bashrc').mksymlinkto(repodir.ensure('bashrc'))
    tmpdir.join('.inputrc').mksymlinkto(repodir.ensure('inputrc'))
    tmpdir.join('.vimrc').mksymlinkto(repodir.ensure('vimrc'))

    repo = Repository(repodir, tmpdir)

    expected_status = ("{1:<18} {0}\n"
                       "{2:<18} {0}\n"
                       "{3:<18} {0}".format(Dotfile.states['ok']['text'],
                                            '.bashrc',
                                            '.inputrc',
                                            '.vimrc'))

    assert expected_status == repo.status()


def test_check(tmpdir, monkeypatch):

    repodir = tmpdir.join('repo')

    dotfile_a = Dotfile(tmpdir.join('.aaa'), repodir.join('aaa'))
    dotfile_b = Dotfile(tmpdir.join('.bbb'), repodir.join('bbb'))
    dotfile_c = Dotfile(tmpdir.join('.ccc'), repodir.join('ccc'))

    dotfile_b.state = Dotfile.states['ok']

    repo = Repository(tmpdir)
    monkeypatch.setattr(Repository, "_load",
                        lambda self: [dotfile_a, dotfile_b, dotfile_c])

    expected_status = ("{1:<18} {0}\n"
                       "{2:<18} {0}".format(Dotfile.states['error']['text'],
                                            dotfile_a.name.basename,
                                            dotfile_c.name.basename))

    assert expected_status == repo.check()


def test_sync():
    with pytest.raises(NotImplementedError):
        Repository('todo').sync()


def test_unsync():
    with pytest.raises(NotImplementedError):
        Repository('todo').unsync()


def test_add():
    with pytest.raises(NotImplementedError):
        Repository('todo').add()


def test_remove():
    with pytest.raises(NotImplementedError):
        Repository('todo').remove()


def test_move():
    with pytest.raises(NotImplementedError):
        Repository('todo').move()
