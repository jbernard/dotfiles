import pytest
from click.testing import CliRunner


@pytest.fixture(scope='function')
def home(request, tmpdir):
    return tmpdir.ensure('home', dir=1)


@pytest.fixture(scope='function')
def repo(request, tmpdir):
    return tmpdir.ensure('repo', dir=1)


@pytest.fixture(scope='function')
def runner(request):
    return CliRunner()
