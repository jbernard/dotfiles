from dotfiles.core import Dotfiles


def test_sync(tmpdir):
    """Basic sync operation."""

    dotfile = tmpdir.ensure('Dotfiles/foo')
    symlink = tmpdir.join('.foo')

    Dotfiles(homedir=str(tmpdir),
             path=str(dotfile.dirname),
             prefix='',
             ignore=[],
             externals={},
             packages=[],
             dry_run=False).sync()

    assert symlink.check(link=1)
    assert symlink.samefile(dotfile)
