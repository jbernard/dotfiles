class DotfileException(Exception):
    """An exception the CLI can handle and show to the user."""

    def __init__(self, path, message='an unknown error occurred'):
        self.message = '\'%s\' %s' % (path, message)
        Exception.__init__(self, self.message)

    def __str__(self):
        return 'ERROR: %s' % self.message


class TargetIgnored(DotfileException):

    def __init__(self, path):
        DotfileException.__init__(self, path, 'targets an ignored file')


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


class IsNested(DotfileException):

    def __init__(self, path):
        DotfileException.__init__(self, path, 'is nested')


class NotADotfile(DotfileException):

    def __init__(self, path):
        DotfileException.__init__(self, path, 'is not a dotfile')


class DoesNotExist(DotfileException):

    def __init__(self, path):
        DotfileException.__init__(self, path, 'doest not exist')


class TargetExists(DotfileException):

    def __init__(self, path):
        DotfileException.__init__(self, path, 'target already exists')


class TargetMissing(DotfileException):

    def __init__(self, path):
        DotfileException.__init__(self, path, 'target is missing')
