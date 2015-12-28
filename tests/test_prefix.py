import pytest
from dotfiles.core import Dotfiles


@pytest.mark.xfail()
def test_prefix(tmpdir):
    """Test basic sync when using a non-default prefix."""

    dotfile = tmpdir.ensure('Dotfiles/_vimrc')
    symlink = tmpdir.join('.vimrc')

    Dotfiles(homedir=str(tmpdir),
             path=str(dotfile.dirname),
             prefix='_',
             ignore=[],
             externals={},
             packages=[],
             dry_run=False).sync()

    assert symlink.check(link=1)
    assert symlink.samefile(dotfile)


def test_prefix_with_package(tmpdir):
    """Test syncing a package when using a non-default prefix."""

    repository = tmpdir.ensure('Dotfiles', dir=1)
    dotfile = repository.ensure('.config/awesome/testfile')

    Dotfiles(homedir=str(tmpdir),
             path=str(repository),
             prefix='.',
             ignore=[],
             externals={},
             packages=['.config'],
             dry_run=False,
             quiet=True).sync()

    assert tmpdir.join('.config').check(dir=1)
    assert tmpdir.join('.config/awesome').check(link=1)
    assert tmpdir.join('.config/awesome').samefile(dotfile.dirname)
