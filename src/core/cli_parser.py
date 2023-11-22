from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from typing import Any

from typing_extensions import override

from ..version import __version__

__all__ = ["Args", "parser", "check_args"]


@dataclass
class Args:
    cfg_path: str = ".cfg"
    debug: bool = False
    usernames: str = "assets/user.txt"
    passwords: str = "assets/passwd.txt"
    it_comb: tuple[int, int] = (3, 2)
    each: int = 1000
    timeout: int = 10
    max_tries: int = 3
    threads: int = 50
    sleep: int = 0
    use_all: bool = False


class WeakParser(ArgumentParser):
    @override
    def add_argument(self, *args: Any, **kwargs: Any) -> "WeakParser":
        kwargs["default"] = None
        super().add_argument(*args, **kwargs)
        return self

    def add_path_argument(self, *args: Any, **kwargs: Any) -> "WeakParser":
        kwargs["metavar"] = "P"
        kwargs["type"] = str
        super().add_argument(*args, **kwargs)
        return self

    def add_int_argument(self, *args: Any, **kwargs: Any) -> "WeakParser":
        kwargs["metavar"] = "N"
        kwargs["type"] = int
        super().add_argument(*args, **kwargs)
        return self


def parse_it_comb(it_comb: str) -> tuple[int, int]:
    # parse from "1, 2" to (1, 2)
    # parse from "1" to (1, 1)
    parts = list(map(lambda s: s.strip(), it_comb.split(",")))
    if len(parts) == 1:
        return (int(parts[0]), int(parts[0]))
    elif len(parts) == 2:
        return (int(parts[0]), int(parts[1]))
    return  # leave blank since argparse does not reraise


def parser() -> WeakParser:
    parser = WeakParser(
        description="A simple CLI to bruteforce login forms",
        epilog="visit us on GitHub : https://github.com/ThomasByr/tor-brute",
    )
    return (
        parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")
        .add_path_argument("-c", "--config", dest="cfg_path", help="Path to the config file")
        .add_path_argument(
            "-u",
            "--user",
            dest="usernames",
            help="Path to the usernames text file (one username-part per line))",
        )
        .add_path_argument(
            "-p",
            "--passwd",
            dest="passwords",
            help="Path to the passwords text file (one password-part per line)",
        )
        .add_argument(
            "-i",
            "--iter",
            dest="it_comb",
            metavar="N[, M]",
            type=parse_it_comb,
            help="how much to iterate over the combinations (default: 3, 2 for user, passwd)",
        )
        .add_int_argument(
            "-e",
            "--each",
            dest="each",
            help="each how many requests to change the Tor identity (default: 1000)",
        )
        .add_int_argument(
            "-t",
            "--timeout",
            dest="timeout",
            help="how much to wait for a response in seconds (default: 10)",
        )
        .add_int_argument(
            "-m",
            "--max-tries",
            dest="max_tries",
            help="how much to try to reconnect to the target and how many consecutive fail to consider before killing the app (default: 3)",
        )
        .add_int_argument("-w", "--threads", dest="threads", help="how much threads to use (default: 50)")
        .add_int_argument(
            "-s",
            "--sleep",
            dest="sleep",
            help="how much to sleep between each Tor identity swap (default: 0)",
        )
        .add_argument(
            "-a",
            "--all",
            dest="use_all",
            action="store_true",
            help="use all the possible permutations instead of the faster unordered classic (default: False)",
        )
        .add_argument("-d", "--debug", dest="debug", action="store_true", help="Enable debug mode")
    )


def check_path(path: str, mode: str = "r") -> str:
    """Check if the path exists"""
    try:
        with open(path, mode, encoding="utf-8"):
            return path
    except FileNotFoundError as e:
        raise ValueError(f"file {path} does not exist") from e
    except PermissionError as e:
        raise ValueError(f"file {path} is not can not be opened in [{mode}] mode") from e
    except IsADirectoryError as e:
        raise ValueError(f"file {path} is a directory") from e
    except OSError as e:
        raise ValueError(f"file {path} is not a file") from e
    except Exception as e:
        raise ValueError(f"unknown error with file {path}") from e


def check_args(args: Namespace) -> Args:
    MINIMUM_EACH_VALUE = 100
    a = Args()

    # paths (and read property)
    if args.cfg_path is not None:
        a.cfg_path = check_path(args.cfg_path)
    if args.usernames is not None:
        a.usernames = check_path(args.usernames)
    if args.passwords is not None:
        a.passwords = check_path(args.passwords)

    if args.it_comb is not None:
        if any(i < 1 for i in args.it_comb):
            raise ValueError("[--iter] values must be >= 1")
        a.it_comb = args.it_comb
    if args.each is not None:
        if 0 < args.each < MINIMUM_EACH_VALUE:
            raise ValueError("[--each] value must be at least >= %d", MINIMUM_EACH_VALUE)
        a.each = args.each
    if args.timeout is not None:
        if args.timeout < 1:
            raise ValueError("[--timeout] value must be >= 1")
        a.timeout = args.timeout
    if args.max_tries is not None:
        if args.max_tries < 1:
            raise ValueError("[--max-tries] value must be >= 1")
        a.max_tries = args.max_tries
    if args.threads is not None:
        if args.threads < 1:
            raise ValueError("[--threads] value must be >= 1")
        a.threads = args.threads
    if args.sleep is not None:
        if args.sleep < 0:
            raise ValueError("[--sleep] value must be >= 0")
        a.sleep = args.sleep
    if args.use_all is not None:
        a.use_all = args.use_all
    if args.debug:
        a.debug = args.debug
    return a
