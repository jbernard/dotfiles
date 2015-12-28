from dotfiles.core import Dotfiles


def test_package_sync(tmpdir):
    """Test syncing a package."""

    repository = tmpdir.ensure('Dotfiles', dir=1)
    dotfile = repository.ensure('config/awesome/testfile')

    Dotfiles(homedir=str(tmpdir),
             path=str(repository),
             prefix='',
             ignore=[],
             externals={},
             packages=['config'],
             dry_run=False,
             quiet=True).sync()

    assert tmpdir.join('.config').check(dir=1)
    assert tmpdir.join('.config/awesome').check(link=1)
    assert tmpdir.join('.config/awesome').samefile(dotfile.dirname)
