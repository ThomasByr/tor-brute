from argparse import ArgumentParser, FileType, Namespace
from dataclasses import dataclass
from typing import Any

from typing_extensions import override

from ..version import __version__

__all__ = ["Args", "parser", "check_args"]


@dataclass
class Args:
    cfg_path: str = ".cfg"
    debug: bool = False
    usernames: str = "assets/users.txt"
    passwords: str = "assets/passwd.txt"
    it_comb: tuple[int, int] = (3, 2)
    each: int = 1000


class WeakParser(ArgumentParser):
    @override
    def add_argument(self, *args: Any, **kwargs: Any) -> "WeakParser":
        kwargs["default"] = None
        super().add_argument(*args, **kwargs)
        return self

    def add_path_argument(self, *args: Any, **kwargs: Any) -> "WeakParser":
        kwargs["metavar"] = "P"
        kwargs["type"] = FileType("r")
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
    raise ValueError("invalid it_comb value")


def parser() -> WeakParser:
    parser = WeakParser(
        description="A simple CLI to bruteforce login forms",
        epilog="visit us on GitHub : https://github.com/ThomasByr/tor-brute",
    )
    return (
        parser.add_argument(
            "-v",
            "--version",
            action="version",
            version=f"%(prog)s {__version__}",
        )
        .add_path_argument(
            "-c",
            "--config",
            dest="cfg_path",
            help="Path to the config file",
        )
        .add_path_argument(
            "-u",
            "--user",
            dest="usernames",
            help="Path to the usernames text file",
        )
        .add_path_argument(
            "-p",
            "--passwd",
            dest="passwords",
            help="Path to the passwords text file",
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
        .add_argument(
            "-d",
            "--debug",
            dest="debug",
            action="store_true",
            help="Enable debug mode",
        )
    )


def check_args(args: Namespace) -> Args:
    MINIMUM_EACH_VALUE = 100
    a = Args()

    # paths (and read property) are checked by the ArgParser
    if args.cfg_path is not None:
        a.cfg_path = args.cfg_path
    if args.usernames is not None:
        a.usernames = args.usernames
    if args.passwords is not None:
        a.passwords = args.passwords

    if args.it_comb is not None:
        if any(i < 1 for i in args.it_comb):
            raise ValueError("[--iter] values must be >= 1")
        a.it_comb = args.it_comb
    if args.each is not None:
        if 0 < args.each < MINIMUM_EACH_VALUE:
            raise ValueError(
                "[--each] value must be at least >= %d", MINIMUM_EACH_VALUE
            )
        a.each = args.each
    if args.debug:
        a.debug = args.debug
    return a
