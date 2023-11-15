from argparse import ArgumentParser, Namespace
from dataclasses import dataclass

from ..version import __version__

__all__ = ["Args", "parser", "check_args"]


@dataclass
class Args:
    cfg_path: str
    debug: bool
    usernames: str
    passwords: str
    it_comb: tuple[int, int]


def parse_it_comb(it_comb: str) -> tuple[int, int]:
    # parse from "1, 2" to (1, 2)
    # parse from "1" to (1, 1)
    parts = list(map(lambda s: s.strip(), it_comb.split(",")))
    if len(parts) == 1:
        return (int(parts[0]), int(parts[0]))
    elif len(parts) == 2:
        return (int(parts[0]), int(parts[1]))


def parser() -> Namespace:
    parser = ArgumentParser(
        description="A simple CLI to bruteforce login forms",
        epilog="visit us on GitHub : https://github.com/ThomasByr/tor-brute",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "-c",
        "--config",
        dest="cfg_path",
        default=None,
        help="Path to the config file",
    )
    parser.add_argument(
        "-u",
        "--users",
        dest="usernames",
        default=None,
        help="Path to the usernames text file",
    )
    parser.add_argument(
        "-p",
        "--passwd",
        dest="passwords",
        default=None,
        help="Path to the passwords text file",
    )
    parser.add_argument(
        "-i",
        "--iter",
        dest="it_comb",
        default=None,
        type=parse_it_comb,
        help="how much to iterate over the combinations (default: 3, 2 for user, passwd)",
    )
    parser.add_argument(
        "-d",
        "--debug",
        dest="debug",
        action="store_true",
        help="Enable debug mode",
    )

    return parser.parse_args()


def check_args(args: Namespace) -> Args:
    return Args(
        cfg_path=args.cfg_path or ".cfg",
        debug=args.debug or False,
        usernames=args.usernames or "assets/users.txt",
        passwords=args.passwords or "assets/passwd.txt",
        it_comb=args.it_comb or (3, 2),
    )
