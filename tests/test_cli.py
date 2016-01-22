from dotfiles.cli import cli
from dotfiles.repository import Repository


class TestCli(object):

    def test_status(self, runner, repo, monkeypatch):

        def repo_init(self, *args, **kwargs):
            self.path = repo.path.ensure_dir()
            self.homedir = repo.homedir
            self.ignore_patterns = repo.ignore_patterns
            self.preserve_leading_dot = repo.preserve_leading_dot

        monkeypatch.setattr(Repository, '__init__', repo_init)

        result = runner.invoke(cli, ['status'])
        assert not result.exception
        assert result.output == ''
