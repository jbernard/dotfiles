# -*- coding: utf-8 -*-

"""
dotfiles.core
~~~~~~~~~~~~~

This module provides the basic functionality of dotfiles.
"""

import os
import os.path
import shutil
import fnmatch


__version__ = '0.5.5'
__author__ = 'Jon Bernard'
__license__ = 'ISC'

if hasattr(os, 'symlink'):
    symlink = os.symlink
    islink = os.path.islink
    realpath = os.path.realpath
else:
    # Windows symlinks -- ctypes version
    # symlink, islink, readlink, realpath, is_link_to

    win32_verbose = False       # set to True to debug symlink stuff
    import os, ctypes, struct
    from ctypes import windll, wintypes

    FSCTL_GET_REPARSE_POINT = 0x900a8

    FILE_ATTRIBUTE_READONLY      = 0x0001
    FILE_ATTRIBUTE_HIDDEN        = 0x0002
    FILE_ATTRIBUTE_DIRECTORY     = 0x0010
    FILE_ATTRIBUTE_NORMAL        = 0x0080
    FILE_ATTRIBUTE_REPARSE_POINT = 0x0400


    GENERIC_READ  = 0x80000000
    GENERIC_WRITE = 0x40000000
    OPEN_EXISTING = 3
    FILE_READ_ATTRIBUTES = 0x80
    FILE_FLAG_OPEN_REPARSE_POINT = 0x00200000
    INVALID_HANDLE_VALUE = wintypes.HANDLE(-1).value

    INVALID_FILE_ATTRIBUTES = 0xFFFFFFFF

    FILE_FLAG_OPEN_REPARSE_POINT = 2097152
    FILE_FLAG_BACKUP_SEMANTICS = 33554432
    # FILE_FLAG_OPEN_REPARSE_POINT | FILE_FLAG_BACKUP_SEMANTI
    FILE_FLAG_REPARSE_BACKUP = 35651584


    kdll = windll.LoadLibrary("kernel32.dll")
    CreateSymbolicLinkA = windll.kernel32.CreateSymbolicLinkA
    CreateSymbolicLinkA.restype = wintypes.BOOLEAN
    CreateSymbolicLinkW = windll.kernel32.CreateSymbolicLinkW
    CreateSymbolicLinkW.restype = wintypes.BOOLEAN
    GetFileAttributesA = windll.kernel32.GetFileAttributesA
    GetFileAttributesW = windll.kernel32.GetFileAttributesW
    CloseHandle = windll.kernel32.CloseHandle
    _CreateFileW = windll.kernel32.CreateFileW
    _CreateFileA = windll.kernel32.CreateFileA
    _DevIoCtl = windll.kernel32.DeviceIoControl
    _DevIoCtl.argtypes = [
        wintypes.HANDLE, #HANDLE hDevice
        wintypes.DWORD, #DWORD dwIoControlCode
        wintypes.LPVOID, #LPVOID lpInBuffer
        wintypes.DWORD, #DWORD nInBufferSize
        wintypes.LPVOID, #LPVOID lpOutBuffer
        wintypes.DWORD, #DWORD nOutBufferSize
        ctypes.POINTER(wintypes.DWORD), #LPDWORD lpBytesReturned
        wintypes.LPVOID] #LPOVERLAPPED lpOverlapped
    _DevIoCtl.restype = wintypes.BOOL


    def CreateSymbolicLink(name, target, is_dir):
        assert type(name) == type(target)
        if type(name) == unicode:
            stat = CreateSymbolicLinkW(name, target, is_dir)
        else:
            stat = CreateSymbolicLinkA(name, target, is_dir)
        if win32_verbose:
            print "CreateSymbolicLink(name=%s, target=%s, is_dir=%d) = %#x"%(name,target,is_dir, stat)
        if not stat:
            print "Can't create symlink %s -> %s"%(name, target)
            raise ctypes.WinError()

    def symlink(target, name):
        CreateSymbolicLink(name, target, 0)

    def GetFileAttributes(path):
        if type(path) == unicode:
            return GetFileAttributesW(path)
        else:
            return GetFileAttributesA(path)

    def islink(path):
        assert path
        has_link_attr = GetFileAttributes(path) & FILE_ATTRIBUTE_REPARSE_POINT
        if win32_verbose:
            print "islink(%s): attrs=%#x: %s"%(path, GetFileAttributes(path), has_link_attr != 0)
        return has_link_attr != 0

    def DeviceIoControl(hDevice, ioControlCode, input, output):
        # DeviceIoControl Function
        # http://msdn.microsoft.com/en-us/library/aa363216(v=vs.85).aspx
        if input:
            input_size = len(input)
        else:
            input_size = 0
        if isinstance(output, int):
            output = ctypes.create_string_buffer(output)
        output_size = len(output)
        assert isinstance(output, ctypes.Array)
        bytesReturned = wintypes.DWORD()
        status = _DevIoCtl(hDevice, ioControlCode, input,
                           input_size, output, output_size, bytesReturned, None)
        if win32_verbose:
            print "DeviceIOControl: status = %d" % status
        if status != 0:
            return output[:bytesReturned.value]
        else:
            return None


    def CreateFile(path, access, sharemode, creation, flags):
        if type(path) == unicode:
            return _CreateFileW(path, access, sharemode, None, creation, flags, None)
        else:
            return _CreateFileA(path, access, sharemode, None, creation, flags, None)

    SymbolicLinkReparseFormat = "LHHHHHHL"
    SymbolicLinkReparseSize = struct.calcsize(SymbolicLinkReparseFormat);

    def readlink(path):
        """ Windows readlink implementation. """
        # This wouldn't return true if the file didn't exist, as far as I know.
        if not islink(path):
            if win32_verbose:
                print "readlink(%s): not a link."%path
            return None

        # Open the file correctly depending on the string type.
        hfile = CreateFile(path, GENERIC_READ, 0, OPEN_EXISTING, FILE_FLAG_OPEN_REPARSE_POINT)

        # MAXIMUM_REPARSE_DATA_BUFFER_SIZE = 16384 = (16*1024)
        buffer = DeviceIoControl(hfile, FSCTL_GET_REPARSE_POINT, None, 16384)
        CloseHandle(hfile)

        # Minimum possible length (assuming length of the target is bigger than 0)
        if not buffer or len(buffer) < 9:
            if win32_verbose:
                print "readlink(%s): no reparse buffer."%path
            return None

        # Parse and return our result.
        # typedef struct _REPARSE_DATA_BUFFER {
        #   ULONG  ReparseTag;
        #   USHORT ReparseDataLength;
        #   USHORT Reserved;
        #   union {
        #       struct {
        #           USHORT SubstituteNameOffset;
        #           USHORT SubstituteNameLength;
        #           USHORT PrintNameOffset;
        #           USHORT PrintNameLength;
        #           ULONG Flags;
        #           WCHAR PathBuffer[1];
        #       } SymbolicLinkReparseBuffer;
        #       struct {
        #           USHORT SubstituteNameOffset;
        #           USHORT SubstituteNameLength;
        #           USHORT PrintNameOffset;
        #           USHORT PrintNameLength;
        #           WCHAR PathBuffer[1];
        #       } MountPointReparseBuffer;
        #       struct {
        #           UCHAR  DataBuffer[1];
        #       } GenericReparseBuffer;
        #   } DUMMYUNIONNAME;
        # } REPARSE_DATA_BUFFER, *PREPARSE_DATA_BUFFER;

        # Only handle SymbolicLinkReparseBuffer
        (tag, dataLength, reserver, SubstituteNameOffset, SubstituteNameLength,
         PrintNameOffset, PrintNameLength,
         Flags) = struct.unpack(SymbolicLinkReparseFormat,
                                buffer[:SymbolicLinkReparseSize])
        # print tag, dataLength, reserver, SubstituteNameOffset, SubstituteNameLength
        start = SubstituteNameOffset + SymbolicLinkReparseSize
        actualPath = buffer[start : start + SubstituteNameLength].decode("utf-16")
        # This utf-16 string is null terminated
        index = actualPath.find(u"\0")
        if index > 0:
            actualPath = actualPath[:index]
        if actualPath.startswith(u"\\??\\"): # ASCII 92, 63, 63, 92
            ret = actualPath[4:]             # strip off leading junk
        else:
            ret = actualPath
        if win32_verbose:
            print "readlink(%s->%s->%s): index(null) = %d"%\
                (path,repr(actualPath),repr(ret),index)
        return ret

    def realpath(fpath):
        while islink(fpath):
            rpath = readlink(fpath)
            if rpath is None:
                return fpath
            if not os.path.isabs(rpath):
                rpath = os.path.abspath(os.path.join(os.path.dirname(fpath), rpath))
            fpath = rpath
        return fpath


def is_link_to(path, target):
    def normalize(path):
        return os.path.normcase(os.path.normpath(path))
    return islink(path) and \
        normalize(realpath(path)) == normalize(target)

class Dotfile(object):

    def __init__(self, name, target, home):
        if name.startswith('/'):
            self.name = name
        else:
            self.name = home + '/.%s' % name.strip('.')
        self.basename = os.path.basename(self.name)
        self.target = target.rstrip('/')
        self.status = ''
        if not os.path.lexists(self.name):
            self.status = 'missing'
        elif not is_link_to(self.name, self.target):
            self.status = 'unsynced'

    def sync(self, force):
        if self.status == 'missing':
            symlink(self.target, self.name)
        elif self.status == 'unsynced':
            if not force:
                print("Skipping \"%s\", use --force to override"
                        % self.basename)
                return
            if os.path.isdir(self.name) and not os.path.islink(self.name):
                shutil.rmtree(self.name)
            else:
                os.remove(self.name)
            symlink(self.target, self.name)

    def add(self):
        if self.status == 'missing':
            print("Skipping \"%s\", file not found" % self.basename)
            return
        if self.status == '':
            print("Skipping \"%s\", already managed" % self.basename)
            return
        shutil.move(self.name, self.target)
        symlink(self.target, self.name)

    def remove(self):
        if self.status != '':
            print("Skipping \"%s\", file is %s" % (self.basename, self.status))
            return
        os.remove(self.name)
        shutil.move(self.target, self.name)

    def __str__(self):
        return '%-18s %-s' % (self.name.split('/')[-1], self.status)


class Dotfiles(object):
    """A Dotfiles Repository."""

    __attrs__ = ['homedir', 'repository', 'prefix', 'ignore', 'externals']

    def __init__(self, **kwargs):

        # Map args from kwargs to instance-local variables
        for k, v in kwargs.items():
            if k in self.__attrs__:
                setattr(self, k, v)

        self._load()

    def _load(self):
        """Load each dotfile in the repository."""

        self.dotfiles = list()

        all_repofiles = os.listdir(self.repository)
        repofiles_to_symlink = set(all_repofiles)

        for pat in self.ignore:
            repofiles_to_symlink.difference_update(
                    fnmatch.filter(all_repofiles, pat))

        for dotfile in repofiles_to_symlink:
            self.dotfiles.append(Dotfile(dotfile[len(self.prefix):],
                os.path.join(self.repository, dotfile), self.homedir))

        for dotfile in self.externals.keys():
            self.dotfiles.append(Dotfile(dotfile,
                os.path.expanduser(self.externals[dotfile]),
                self.homedir))

    def _fqpn(self, dotfile):
        """Return the fully qualified path to a dotfile."""

        return os.path.join(self.repository,
                            self.prefix + os.path.basename(dotfile).strip('.'))

    def list(self, verbose=True):
        """List the contents of this repository."""

        for dotfile in sorted(self.dotfiles, key=lambda dotfile: dotfile.name):
            if dotfile.status or verbose:
                print(dotfile)

    def check(self):
        """List only unsynced and/or missing dotfiles."""

        self.list(verbose=False)

    def sync(self, force=False):

        """Synchronize this repository, creating and updating the necessary
        symbolic links."""

        for dotfile in self.dotfiles:
            dotfile.sync(force)

    def add(self, files):
        """Add dotfile(s) to the repository."""

        self._perform_action('add', files)

    def remove(self, files):
        """Remove dotfile(s) from the repository."""

        self._perform_action('remove', files)

    def _perform_action(self, action, files):
        for file in files:
            file = file.rstrip('/')
            if os.path.basename(file).startswith('.'):
                getattr(Dotfile(file, self._fqpn(file), self.homedir), action)()
            else:
                print("Skipping \"%s\", not a dotfile" % file)

    def move(self, target):
        """Move the repository to another location."""

        if os.path.exists(target):
            raise ValueError('Target already exists: %s' % (target))

        shutil.copytree(self.repository, target)
        shutil.rmtree(self.repository)

        self.repository = target

        self._load()
        self.sync(force=True)
