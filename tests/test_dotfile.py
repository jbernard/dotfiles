import pytest
import py.error
from dotfiles.dotfile import Dotfile


class TestAdd:

    def test_add(self, tmpdir):

        repo = tmpdir.ensure("Dotfiles", dir=1)
        name = tmpdir.ensure(".vimrc")
        target = repo.join("vimrc")

        dotfile = Dotfile(name, target)
        dotfile.add()

        assert target.check(file=1, link=0)
        assert name.check(file=1, link=1)
        assert name.samefile(target)

    def test_add_twice(self, tmpdir):

        repo = tmpdir.ensure("Dotfiles", dir=1)
        name = tmpdir.ensure(".vimrc")
        target = repo.join("vimrc")

        dotfile = Dotfile(name, target)
        dotfile.add()

        assert target.check(file=1, link=0)
        assert name.check(file=1, link=1)
        assert name.samefile(target)

        with pytest.raises(OSError):
            dotfile.add()

        assert target.check(file=1, link=0)
        assert name.check(file=1, link=1)
        assert name.samefile(target)


class TestRemove:

    def test_remove(self, tmpdir):

        repo = tmpdir.ensure("Dotfiles", dir=1)
        name = tmpdir.join(".vimrc")
        target = repo.ensure("vimrc")

        name.mksymlinkto(target)

        dotfile = Dotfile(name, target)
        dotfile.remove()

        assert False == target.check()
        assert name.check(file=1, link=0)

    def test_remove_twice(self, tmpdir):

        repo = tmpdir.ensure("Dotfiles", dir=1)
        name = tmpdir.join(".vimrc")
        target = repo.ensure("vimrc")

        name.mksymlinkto(target)

        dotfile = Dotfile(name, target)
        dotfile.remove()

        assert False == target.check()
        assert name.check(file=1, link=0)

        with pytest.raises(OSError):
            dotfile.remove()

        assert False == target.check()
        assert name.check(file=1, link=0)


class TestSync:

    def test_sync(self, tmpdir):

        repo = tmpdir.ensure("Dotfiles", dir=1)
        name = tmpdir.join(".vimrc")
        target = repo.ensure("vimrc")

        dotfile = Dotfile(name, target)
        dotfile.sync()

        assert target.check(file=1, link=0)
        assert name.check(file=1, link=1)
        assert name.samefile(target)

    def test_sync_twice(self, tmpdir):

        repo = tmpdir.ensure("Dotfiles", dir=1)
        name = tmpdir.join(".vimrc")
        target = repo.ensure("vimrc")

        dotfile = Dotfile(name, target)
        dotfile.sync()

        assert target.check(file=1, link=0)
        assert name.check(file=1, link=1)
        assert name.samefile(target)

        with pytest.raises(py.error.EEXIST):
            dotfile.sync()

        assert target.check(file=1, link=0)
        assert name.check(file=1, link=1)
        assert name.samefile(target)
