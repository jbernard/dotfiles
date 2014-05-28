"""
Provides :func:`os.symlink`, :func:`os.path.islink` and
:func:`os.path.realpath` implementations for win32.
"""

import os
import os.path


if hasattr(os, 'symlink'):
    symlink = os.symlink
    islink = os.path.islink
    realpath = os.path.realpath
else:
    # Windows symlinks -- ctypes version
    # symlink, islink, readlink, realpath, is_link_to

    win32_verbose = False       # set to True to debug symlink stuff
    import os
    import ctypes
    import struct
    from ctypes import windll, wintypes

    FSCTL_GET_REPARSE_POINT = 0x900a8

    FILE_ATTRIBUTE_READONLY = 0x0001
    FILE_ATTRIBUTE_HIDDEN = 0x0002
    FILE_ATTRIBUTE_DIRECTORY = 0x0010
    FILE_ATTRIBUTE_NORMAL = 0x0080
    FILE_ATTRIBUTE_REPARSE_POINT = 0x0400

    GENERIC_READ = 0x80000000
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
        wintypes.HANDLE,  # HANDLE hDevice
        wintypes.DWORD,  # DWORD dwIoControlCode
        wintypes.LPVOID,  # LPVOID lpInBuffer
        wintypes.DWORD,  # DWORD nInBufferSize
        wintypes.LPVOID,  # LPVOID lpOutBuffer
        wintypes.DWORD,  # DWORD nOutBufferSize
        ctypes.POINTER(wintypes.DWORD),  # LPDWORD lpBytesReturned
        wintypes.LPVOID]  # LPOVERLAPPED lpOverlapped
    _DevIoCtl.restype = wintypes.BOOL

    def create_symbolic_link(name, target, is_dir):
        assert type(name) == type(target)
        if type(name) == unicode:
            stat = CreateSymbolicLinkW(name, target, is_dir)
        else:
            stat = CreateSymbolicLinkA(name, target, is_dir)
        if win32_verbose:
            print("CreateSymbolicLink(name=%s, target=%s, is_dir=%d) = %#x" % (name, target, is_dir, stat))
        if not stat:
            print("Can't create symlink %s -> %s" % (name, target))
            raise ctypes.WinError()

    def symlink(target, name):
        create_symbolic_link(name, target, 0)

    def get_file_attributes(path):
        if type(path) == unicode:
            return GetFileAttributesW(path)
        else:
            return GetFileAttributesA(path)

    def islink(path):
        assert path
        has_link_attr = get_file_attributes(path) & FILE_ATTRIBUTE_REPARSE_POINT
        if win32_verbose:
            print("islink(%s): attrs=%#x: %s" % (path, get_file_attributes(path), has_link_attr != 0))
        return has_link_attr != 0

    def device_io_control(hdevice, iocontrolcode, input, output):
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
        bytesreturned = wintypes.DWORD()
        status = _DevIoCtl(
            hdevice,
            iocontrolcode,
            input,
            input_size,
            output,
            output_size,
            bytesreturned,
            None
        )
        if win32_verbose:
            print("DeviceIOControl: status = %d" % status)
        if status != 0:
            return output[:bytesreturned.value]
        else:
            return None

    def create_file(path, access, sharemode, creation, flags):
        if type(path) == unicode:
            return _CreateFileW(path, access, sharemode, None, creation, flags, None)
        else:
            return _CreateFileA(path, access, sharemode, None, creation, flags, None)

    SymbolicLinkReparseFormat = "LHHHHHHL"
    SymbolicLinkReparseSize = struct.calcsize(SymbolicLinkReparseFormat)

    def readlink(path):
        """ Windows readlink implementation. """
        # This wouldn't return true if the file didn't exist, as far as I know.
        if not islink(path):
            if win32_verbose:
                print("readlink(%s): not a link." % path)
            return None

        # Open the file correctly depending on the string type.
        hfile = create_file(path, GENERIC_READ, 0, OPEN_EXISTING, FILE_FLAG_OPEN_REPARSE_POINT)

        # MAXIMUM_REPARSE_DATA_BUFFER_SIZE = 16384 = (16*1024)
        buffer = device_io_control(hfile, FSCTL_GET_REPARSE_POINT, None, 16384)
        CloseHandle(hfile)

        # Minimum possible length (assuming length of the target is bigger than 0)
        if not buffer or len(buffer) < 9:
            if win32_verbose:
                print("readlink(%s): no reparse buffer." % path)
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
        (tag, data_length, reserver, substitute_name_offset, substitute_name_length,
         print_name_offset, print_name_length,
         flags) = struct.unpack(SymbolicLinkReparseFormat,
                                buffer[:SymbolicLinkReparseSize])
        # print tag, dataLength, reserver, SubstituteNameOffset, SubstituteNameLength
        start = substitute_name_offset + SymbolicLinkReparseSize
        actual_path = buffer[start: start + substitute_name_length].decode("utf-16")
        # This utf-16 string is null terminated
        index = actual_path.find("\0")
        if index > 0:
            actual_path = actual_path[:index]
        if actual_path.startswith("\\??\\"):  # ASCII 92, 63, 63, 92
            ret = actual_path[4:]             # strip off leading junk
        else:
            ret = actual_path
        if win32_verbose:
            print("readlink(%s->%s->%s): index(null) = %d" %
                  (path, repr(actual_path), repr(ret), index))
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
