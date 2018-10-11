import pytest
from click.testing import CliRunner

from dotfiles.repository import Repository


@pytest.fixture(scope='function', params=['', 'home'])
def repo(request, tmpdir):
    path = tmpdir.ensure_dir('repo')
    home = tmpdir.ensure_dir(request.param)
    return Repository(path, home)


@pytest.fixture(scope='function')
def runner():
    return CliRunner()
