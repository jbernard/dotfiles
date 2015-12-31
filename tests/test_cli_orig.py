from dotfiles.cli_orig import dispatch


def test_dispatch():
    """Test that the force option is handed on to the sync method."""

    class MockDotfiles:
        def sync(self, files=None, force=False):
            assert force

    class MockNamespace:
        def __init__(self):
            self.action = 'sync'
            self.force = True

    dispatch(MockDotfiles(), MockNamespace(), [])
