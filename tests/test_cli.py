from click.testing import CliRunner

from dotfiles import __version__
from dotfiles.cli import version


def test_version():
    runner = CliRunner()
    result = runner.invoke(version)
    assert ('dotfiles v%s\n' % __version__) == result.output
