import sys
from argparse import ArgumentParser
from collections.abc import Sequence
from logging import DEBUG, Formatter, StreamHandler, getLogger
from signal import SIG_IGN, SIGINT, SIGPIPE, SIGTERM, signal
from threading import Event

from .comm import CommAnalyzer, CommKernel, CommMgmt, CommMoninj
from .server import SocketPool

LOGGER = getLogger()
LOGGER_DEFAULT_FMT = "%(relativeCreated)08d | [%(levelname)8s] %(name)s@%(threadName)s: %(message)s"
LOGGER_DEFAULT_DATEFMT = "%Y-%m-%d %H:%M:%S"
LOGGER_DEFAULT_LEVEL = DEBUG


def setup_logger() -> None:
    formatter = Formatter(fmt=LOGGER_DEFAULT_FMT, datefmt=LOGGER_DEFAULT_DATEFMT)
    handler = StreamHandler(sys.stderr)
    handler.setFormatter(formatter)
    LOGGER.addHandler(handler)
    LOGGER.setLevel(LOGGER_DEFAULT_LEVEL)


def main(argv: Sequence[str] | None = None, call_setup_logger: bool = True) -> None:
    if call_setup_logger:
        setup_logger()

    if argv is None:
        argv = sys.argv
    arg_parser = ArgumentParser(prog=argv[0])
    arg_parser.add_argument("-M", "--mgmt-port", default=CommMgmt.DEFAULT_PORT, type=int)
    arg_parser.add_argument("-K", "--kernel-port", default=CommKernel.DEFAULT_PORT, type=int)
    arg_parser.add_argument("-A", "--analyzer-port", default=CommAnalyzer.DEFAULT_PORT, type=int)
    arg_parser.add_argument("-J", "--moninj-port", default=CommMoninj.DEFAULT_PORT, type=int)
    p_args = arg_parser.parse_args(argv[1:])

    pool = SocketPool()
    try:
        pool.add_server(CommMgmt(CommMgmt.DEFAULT_NAME, p_args.mgmt_port))
        pool.add_server(CommKernel(CommKernel.DEFAULT_NAME, p_args.kernel_port))
        pool.add_server(CommAnalyzer(CommAnalyzer.DEFAULT_NAME, p_args.analyzer_port))
        pool.add_server(CommMoninj(CommMoninj.DEFAULT_NAME, p_args.moninj_port))

        stop = Event()
        signal(SIGINT, lambda signalnum, frame: stop.set())
        signal(SIGTERM, lambda signalnum, frame: stop.set())
        signal(SIGPIPE, SIG_IGN)
        while not stop.wait(1):
            pool.collect_garbage()

    finally:
        pool.shutdown()
