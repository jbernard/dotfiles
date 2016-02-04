from dotfiles.cli import cli


class TestCli(object):

    def test_status(self, runner, repo, monkeypatch):

        result = runner.invoke(cli, ['-r', str(repo.path), 'status'])
        assert not result.exception
        assert result.output == ''
