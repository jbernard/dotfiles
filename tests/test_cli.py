from dotfiles.cli import cli
from dotfiles.repository import Repository


class TestCli(object):

    def test_status(self, runner, repo, home, monkeypatch):

        def repo_init(self, *args, **kwargs):
            self.ignore = []
            self.homedir = home
            self.repodir = repo.ensure(dir=1)

        monkeypatch.setattr(Repository, '__init__', repo_init)

        result = runner.invoke(cli, ['status'])
        assert not result.exception
        assert result.output == ''
