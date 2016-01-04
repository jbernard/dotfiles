import pytest
from click.testing import CliRunner


@pytest.fixture(scope='function', params=[''])
def home(request, tmpdir):
    return tmpdir.join(request.param)


@pytest.fixture(scope='function')
def repo(tmpdir):
    return tmpdir.ensure('repo', dir=1)


@pytest.fixture(scope='function')
def runner():
    return CliRunner()
