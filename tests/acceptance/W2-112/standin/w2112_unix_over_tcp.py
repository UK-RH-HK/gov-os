"""Unix sockets carried over loopback TCP, for the W2-112 memory-release cases where ``socket(AF_UNIX)`` is refused.

The launch sandbox refuses ``socket(AF_UNIX)`` (EPERM), so no service can listen there and every case that needs
one fails whatever the code. The memory-release cases (``test_w2_112_memory_release.py``) install this in the
box's processes (the reranker environment, by a ``.pth``; the sessions, by a ``usercustomize``) and in the test's
own process, so that they show red or green for the release itself. ``install()`` does nothing where Unix sockets
are allowed: there the product's own sockets are used, unchanged.

What it does where it acts: a stream socket asked for ``AF_UNIX`` is a loopback TCP socket; ``bind(path)`` binds a
free loopback port and creates ``path`` as a file holding that port (``O_EXCL``, so a second bind fails as on a Unix
socket; its mode by the process's ``umask``); ``connect(path)`` reads the port there (``FileNotFoundError`` when the
file is missing, ``ConnectionRefusedError`` when it is empty or nothing listens). Unlinking the path is unchanged.
Nothing else (a socket's permissions, ``/proc/net/unix``) is emulated: the cases that use it read neither.
"""

import errno
import os
import socket as _socket_module

_Real = _socket_module.socket


def refused() -> bool:
    try:
        _Real(_socket_module.AF_UNIX, _socket_module.SOCK_STREAM).close()
        return False
    except OSError as error:
        return error.errno in (errno.EPERM, errno.EACCES)


def _path(address):
    if isinstance(address, (str, bytes, os.PathLike)):
        return os.fsdecode(address)
    return None


class OverTcp(_Real):
    """``socket.socket``, with a stream ``AF_UNIX`` socket carried over loopback TCP."""

    def __init__(self, family=-1, type=-1, proto=-1, fileno=None):
        self._w2112_unix = fileno is None and family == _socket_module.AF_UNIX
        if self._w2112_unix:
            super().__init__(_socket_module.AF_INET, type, 0)
        else:
            super().__init__(family, type, proto, fileno)

    def bind(self, address):
        path = _path(address) if self._w2112_unix else None
        if path is None:
            return super().bind(address)
        super().bind(("127.0.0.1", 0))
        try:
            descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o666)
        except FileExistsError:
            raise OSError(errno.EADDRINUSE, "Address already in use") from None
        with os.fdopen(descriptor, "w") as out:
            out.write(str(self.getsockname()[1]))

    def connect(self, address):
        path = _path(address) if self._w2112_unix else None
        if path is None:
            return super().connect(address)
        with open(path, encoding="ascii") as found:  # FileNotFoundError when nothing is there, as on a Unix socket
            text = found.read().strip()
        if not text.isdigit():
            raise ConnectionRefusedError(errno.ECONNREFUSED, "Connection refused")
        return super().connect(("127.0.0.1", int(text)))


def install() -> bool:
    """Carry Unix sockets over loopback TCP in this process when it may not make them; whether it did."""
    if _socket_module.socket is OverTcp or not refused():
        return False
    _socket_module.socket = OverTcp
    return True
