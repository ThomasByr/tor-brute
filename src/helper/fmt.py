import logging
import os
import sys
import signal
from typing import Any

from termcolor import colored
from typing_extensions import override

__all__ = ["UsefulFormatter", "UselessHandler"]


if os.name == "nt":
    import msvcrt  # type: ignore # noqa
    import ctypes  # type: ignore # noqa

    class __CursorInfo(ctypes.Structure):
        _fields_ = [("size", ctypes.c_int), ("visible", ctypes.c_byte)]


def hide_cursor():
    if os.name == "nt":
        ci = __CursorInfo()
        handle = ctypes.windll.kernel32.GetStdHandle(-11)
        ctypes.windll.kernel32.GetConsoleCursorInfo(handle, ctypes.byref(ci))
        ci.visible = False
        ctypes.windll.kernel32.SetConsoleCursorInfo(handle, ctypes.byref(ci))
    elif os.name == "posix":
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()


def show_cursor():
    if os.name == "nt":
        ci = __CursorInfo()
        handle = ctypes.windll.kernel32.GetStdHandle(-11)
        ctypes.windll.kernel32.GetConsoleCursorInfo(handle, ctypes.byref(ci))
        ci.visible = True
        ctypes.windll.kernel32.SetConsoleCursorInfo(handle, ctypes.byref(ci))
    elif os.name == "posix":
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()


def formatter(
    c: str,
    colored_output: bool = True,
    name_width: int = 10,
    attrs: list[str] = None,
) -> str:
    if colored_output:
        return (
            f"{colored('%(asctime)s', 'grey', attrs=['bold'])} {colored('%(levelname)8s', c, attrs=attrs)}"
            f"{colored(f'%(name){name_width}s', 'magenta')} %(message)s"
        )
    return f"%(asctime)s %(levelname)8s %(name){name_width}s %(message)s"


class UsefulFormatter(logging.Formatter):
    name_width = 4
    dt_fmt = "%Y-%m-%d %H:%M:%S"

    def __init__(self, *args: Any, colored_output: bool = True, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.colored_output = colored_output

    @override
    def format(self, record: logging.LogRecord) -> str:
        self.name_width = max(len(record.name) + 1, self.name_width)
        formats = {
            logging.DEBUG: formatter("green", self.colored_output, self.name_width),
            logging.INFO: formatter("blue", self.colored_output, self.name_width),
            logging.WARNING: formatter("yellow", self.colored_output, self.name_width),
            logging.ERROR: formatter("red", self.colored_output, self.name_width),
            logging.CRITICAL: formatter(
                "red", self.colored_output, self.name_width, ["bold"]
            ),
        }
        log_fmt = formats.get(record.levelno)
        fmt = logging.Formatter(log_fmt, self.dt_fmt, style="%")
        return fmt.format(record)


class UselessHandler(logging.StreamHandler):
    @override
    def emit(self, record: logging.LogRecord) -> None:
        super().emit(record)
        if record.levelno >= logging.CRITICAL:  # exit on critical errors
            show_cursor()
            os.kill(os.getpid(), signal.SIGTERM)
