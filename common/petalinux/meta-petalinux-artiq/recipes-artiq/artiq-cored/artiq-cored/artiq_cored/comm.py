from logging import Logger, getLogger
from socket import AF_INET6, SHUT_RDWR, create_server, socket
from threading import Semaphore, Thread, current_thread
from typing import Callable, Self


class _SocketThread:
    def __init__(self, name: str, sock: socket, thread: Thread) -> None:
        self._name = name
        self._sock: socket | None = sock
        self._thread = thread
        self._logger = getLogger(name)
        self._sem = Semaphore()
        self._thread.start()

    @property
    def is_alive(self) -> bool:
        return self._thread.is_alive()

    def shutdown(self) -> None:
        with self._sem:
            if self._sock is not None:
                self._logger.info("Shutdown")
                try:
                    self._sock.shutdown(SHUT_RDWR)
                except OSError:
                    pass
                self._sock = None
        self._thread.join()


class SocketThreadPool:
    def __init__(self) -> None:
        self._sem = Semaphore()
        self._list: list[_SocketThread] = []
        self._next_id = 1

    def new(self, name: str, sock: socket, handler: Callable[[Self, socket], None]) -> None:
        self.collect_garbage()
        with self._sem:
            t_name = f"T-{name}#{self._next_id}"
            self._list.append(_SocketThread(t_name, sock, Thread(target=handler, name=t_name, args=(self, sock))))
            self._next_id += 1

    def collect_garbage(self) -> None:
        with self._sem:
            garbage_indices = [i for i, st in enumerate(self._list) if not st.is_alive]
            garbage = [self._list.pop(i) for i in reversed(garbage_indices)]
        for st in garbage:
            st.shutdown()

    def shutdown(self) -> None:
        with self._sem:
            garbage = self._list.copy()
            self._list.clear()
        for st in garbage:
            st.shutdown()


class _Comm:
    def __init__(self) -> None:
        pass

    def __call__(self, pool: SocketThreadPool, c_sock: socket) -> None:
        logger = getLogger(current_thread().name)
        try:
            logger.info("New client: %s", c_sock.getpeername())
            self._handle_client(logger, c_sock)
            try:
                c_sock.shutdown(SHUT_RDWR)
            except OSError:
                pass
        finally:
            logger.info("Session ended")

    def _handle_client(self, logger: Logger, c_sock: socket) -> None:
        raise NotImplementedError()


class CommMgmt(_Comm):
    DEFAULT_NAME = "mgmt"
    DEFAULT_PORT = 1380

    def _handle_client(self, logger: Logger, c_sock: socket) -> None:
        pass


class CommKernel(_Comm):
    DEFAULT_NAME = "kernel"
    DEFAULT_PORT = 1381

    def _handle_client(self, logger: Logger, c_sock: socket) -> None:
        pass


class CommAnalyzer(_Comm):
    DEFAULT_NAME = "analyzer"
    DEFAULT_PORT = 1382

    def _handle_client(self, logger: Logger, c_sock: socket) -> None:
        pass


class CommMoninj(_Comm):
    DEFAULT_NAME = "moninj"
    DEFAULT_PORT = 1383

    def _handle_client(self, logger: Logger, c_sock: socket) -> None:
        pass


class Server:
    def __init__(self, name: str, port: int, handle_client: _Comm) -> None:
        self._name = name
        self._handle_client = handle_client
        self._s_sock = create_server(("", port), family=AF_INET6, dualstack_ipv6=True)

    @property
    def s_name(self) -> str:
        return f"server/{self._name}"

    @property
    def c_name(self) -> str:
        return f"client/{self._name}"

    def __call__(self) -> tuple[str, socket, Callable[[SocketThreadPool, socket], None]]:
        return self.s_name, self._s_sock, self._handle_server

    def _handle_server(self, pool: SocketThreadPool, s_sock: socket) -> None:
        logger = getLogger(current_thread().name)
        try:
            logger.info("Listening; port=%d", self._s_sock.getsockname()[1])
            while True:
                c_sock, _ = s_sock.accept()
                pool.new(self.c_name, c_sock, self._handle_client)
        except OSError:
            pass
