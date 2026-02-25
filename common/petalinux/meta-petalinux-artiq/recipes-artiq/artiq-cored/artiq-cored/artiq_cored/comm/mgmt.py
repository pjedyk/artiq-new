from socket import socket

from ..server import Server


class CommMgmt(Server):
    DEFAULT_NAME = "mgmt"
    DEFAULT_PORT = 1380

    def _handle_client(self, c_sock: socket) -> None:
        pass
