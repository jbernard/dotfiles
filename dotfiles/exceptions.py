class DotfileException(Exception):
    """An exception the CLI can handle and show to the user."""
    def __init__(self, path, message='an unknown error occurred'):
        self.message = '\'%s\' %s' % (path, message)
        Exception.__init__(self, self.message)

    def __str__(self):
        return 'ERROR: %s' % self.message


class IsDirectory(DotfileException):
    def __init__(self, path):
        DotfileException.__init__(self, path, 'is a directory')


class IsSymlink(DotfileException):
    def __init__(self, path):
        DotfileException.__init__(self, path, 'is a symlink')


class NotASymlink(DotfileException):
    def __init__(self, path):
        DotfileException.__init__(self, path, 'is not a symlink')


class InRepository(DotfileException):
    def __init__(self, path):
        DotfileException.__init__(self, path, 'is within the repository')


class NotRootedInHome(DotfileException):
    def __init__(self, path):
        DotfileException.__init__(self, path, 'not rooted in home directory')


class Exists(DotfileException):
    def __init__(self, path):
        DotfileException.__init__(self, path, 'already exists')


class NotFound(DotfileException):
    def __init__(self, path):
        DotfileException.__init__(self, path, 'not found')


class Dangling(DotfileException):
    def __init__(self, path):
        DotfileException.__init__(self, path, 'is a dangling symlink')


class TargetIgnored(DotfileException):
    def __init__(self, path):
        DotfileException.__init__(self, path, 'targets an ignored file')


class TargetExists(DotfileException):
    def __init__(self, path):
        DotfileException.__init__(self, path, 'target already exists')


class TargetMissing(DotfileException):
    def __init__(self, path):
        DotfileException.__init__(self, path, 'target is missing')
