from socket import socket

from ..server import Server


class CommMoninj(Server):
    DEFAULT_NAME = "moninj"
    DEFAULT_PORT = 1383

    def _handle_client(self, c_sock: socket) -> None:
        pass
