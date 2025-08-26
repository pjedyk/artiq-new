import sys
from argparse import ArgumentParser
from collections.abc import Sequence
from logging import DEBUG, Formatter, StreamHandler, getLogger
from signal import SIG_IGN, SIGINT, SIGPIPE, SIGTERM, signal
from threading import Event

from .comm import CommAnalyzer, CommKernel, CommMgmt, CommMoninj, Server, SocketThreadPool

LOGGER = getLogger()
LOGGER_DEFAULT_FMT = "%(relativeCreated)08d | %(levelname)8s | %(name)s : %(message)s"
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

    pool = SocketThreadPool()
    try:
        pool.new(*Server(CommMgmt.DEFAULT_NAME, p_args.mgmt_port, CommMgmt())())
        pool.new(*Server(CommKernel.DEFAULT_NAME, p_args.kernel_port, CommKernel())())
        pool.new(*Server(CommAnalyzer.DEFAULT_NAME, p_args.analyzer_port, CommAnalyzer())())
        pool.new(*Server(CommMoninj.DEFAULT_NAME, p_args.moninj_port, CommMoninj())())

        stop = Event()
        signal(SIGINT, lambda signalnum, frame: stop.set())
        signal(SIGTERM, lambda signalnum, frame: stop.set())
        signal(SIGPIPE, SIG_IGN)
        while not stop.wait(1):
            pool.collect_garbage()

    finally:
        pool.shutdown()
