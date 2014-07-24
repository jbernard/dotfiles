from dotfiles.core import Dotfiles as Repository


def test_sync(homedir):
    """Basic sync operation."""

    contents = {'.foo': True,
                '.bar': True,
                '.baz': False}

    homedir.setup(contents)

    Repository(path=homedir.repo,
               homedir=homedir.path).sync()

    # .baz should now exist and link to the correct location
    contents['.baz'] = True
    homedir.verify(contents)
