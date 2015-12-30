from dotfiles.dotfile import Dotfile
from dotfiles.repository import Repository


def test_list(tmpdir):

    repo = tmpdir.ensure("Dotfiles", dir=1)
    name = tmpdir.join(".vimrc")
    target = repo.ensure("vimrc")

    dotfile = Dotfile(name, target)
    repository = Repository(repo, tmpdir)

    # manual discovery
    repository.dotfiles = [dotfile, dotfile, dotfile]

    expected_list = (".vimrc -> Dotfiles/vimrc (unknown)\n"
                     ".vimrc -> Dotfiles/vimrc (unknown)\n"
                     ".vimrc -> Dotfiles/vimrc (unknown)")

    assert expected_list == str(repository)


def test_discovery(tmpdir):

    repo = tmpdir.ensure("Dotfiles", dir=1)

    tmpdir.join('.bashrc').mksymlinkto(repo.ensure('bashrc'))
    tmpdir.join('.inputrc').mksymlinkto(repo.ensure('inputrc'))
    tmpdir.join('.vimrc').mksymlinkto(repo.ensure('vimrc'))

    repository = Repository(repo, tmpdir)

    expected_list = (".bashrc -> Dotfiles/bashrc (unknown)\n"
                     ".inputrc -> Dotfiles/inputrc (unknown)\n"
                     ".vimrc -> Dotfiles/vimrc (unknown)")

    assert expected_list == str(repository)
