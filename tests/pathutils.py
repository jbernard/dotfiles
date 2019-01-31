# TODO: docstrings
# XXX: can this move into tests/?


def is_file(path):
    return path.is_file() and not path.is_symlink()


def is_link(path):
    return path.is_file() and path.is_symlink()


def mkdir(path):
    try:
        path.mkdir(parents=True)
    except FileExistsError:
        pass


def touch(path):
    mkdir(path.parent)
    path.touch()
