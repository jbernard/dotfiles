import pytest
from click.testing import CliRunner


@pytest.fixture(scope='function', params=['', 'home'])
def home(request, tmpdir):
    return tmpdir.ensure_dir(request.param)


@pytest.fixture(scope='function')
def repo(tmpdir):
    return tmpdir.ensure_dir('repo')


@pytest.fixture(scope='function')
def runner():
    return CliRunner()
