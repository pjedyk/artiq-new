from socket import socket

from ..server import Server


class CommAnalyzer(Server):
    DEFAULT_NAME = "analyzer"
    DEFAULT_PORT = 1382

    def _handle_client(self, c_sock: socket) -> None:
        pass
