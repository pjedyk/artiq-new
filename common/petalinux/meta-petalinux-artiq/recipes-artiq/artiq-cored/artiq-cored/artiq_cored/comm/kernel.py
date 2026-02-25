from logging import getLogger
from socket import socket
from io import BufferedRWPair
from struct import pack, unpack

from ..server import Server

_LOGGER = getLogger(__name__)


class CommKernel(Server):
    DEFAULT_NAME = "kernel"
    DEFAULT_PORT = 1381

    COREDEV_HELLO = b"ARTIQ coredev\n"
    COREDEV_REPLY = b"e"
    SYNC_CHAR = b"\x5A"
    SYNC_LEN = 4

    def _handle_client(self, c_sock: socket) -> None:
        c_io = c_sock.makefile("brw")

        hello = c_io.read(len(self.COREDEV_HELLO))
        _LOGGER.debug("hello = %r", hello)
        if hello != self.COREDEV_HELLO:
            _LOGGER.warning("Incorrect hello")
            return
        c_io.write(self.COREDEV_REPLY)
        c_io.flush()

        while True:
            req = self._sync(c_io)
            if len(req) == 0:
                return
            _LOGGER.debug("req = 0x%02X", *req)

            req_handler = {
                0x03: self._req_system_info,
                0x05: self._req_load_kernel,
                0x06: self._req_run_kernel,
            }.get(*req)
            if req_handler is None:
                _LOGGER.warning("Invalid request")
                return

            req_handler(c_io)

    def _sync(self, c_io: BufferedRWPair) -> bytes:
        sync = 0
        while True:
            by = c_io.read(1)
            if len(by) == 0:
                return by
            elif by == self.SYNC_CHAR:
                sync += 1
            elif sync < self.SYNC_LEN:
                _LOGGER.warning("No SYNC")
                return b""
            else:
                return by

    def _req_system_info(self, c_io: BufferedRWPair) -> bytes:
        ident = "9.0+unknown.beta;ZynqUS".encode("utf-8")
        c_io.write(self.SYNC_LEN * self.SYNC_CHAR)
        c_io.write(b"\x02")
        c_io.write(b"AROR")
        c_io.write(pack("<I", len(ident)))
        c_io.write(ident)
        c_io.write(b"\x01")
        c_io.flush()

    def _req_load_kernel(self, c_io: BufferedRWPair) -> bytes:
        elf_len, = unpack("<I", c_io.read(4))
        elf_bin = c_io.read(elf_len)
        c_io.write(self.SYNC_LEN * self.SYNC_CHAR)
        c_io.write(b"\x05")
        c_io.flush()

    def _req_run_kernel(self, c_io: BufferedRWPair) -> bytes:
        c_io.write(self.SYNC_LEN * self.SYNC_CHAR)
        c_io.write(b"\x07\x00")
        c_io.flush()
