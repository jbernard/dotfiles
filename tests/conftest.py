import pytest
from click.testing import CliRunner

from dotfiles.repository import Repository


@pytest.fixture(scope='function', params=['', 'home'])
def repo(request, tmpdir):
    path = str(tmpdir.ensure_dir('repo'))
    home = str(tmpdir.ensure_dir(request.param))
    return Repository(path, home)


@pytest.fixture(scope='function')
def runner():
    return CliRunner()
