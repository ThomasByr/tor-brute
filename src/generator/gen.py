import logging
from itertools import combinations
from math import comb
from typing import Generator

__all__ = ["PasswdGenerator"]


class PasswdGenerator:
    def __init__(self, filepath: str = "assets/passwd.txt", max_cmb_len=2) -> None:
        self.__count: int = None
        self.logger = logging.getLogger(".".join(__name__.split(".")[1:]))

        self.max_cmb_len = max_cmb_len
        self.filepath = filepath
        with open(filepath, "r", encoding="utf-8") as f:
            self.chunks = f.read().splitlines(keepends=False)

        # bellow is NOT executed if not debug
        self.logger.debug("[*] %s loaded with %d elements", filepath, self.count)

    def __call__(self) -> Generator[str, None, None]:
        """yields all possible combinations of the chunks"""
        for i in range(1, self.max_cmb_len + 1):
            for combination in combinations(self.chunks, i):
                yield "".join(combination).lower()

    @property
    def count(self) -> int:
        """return the number of possible combinations (cached)"""
        # a, b, c will result in a, b, c, ab, ac, bc, abc
        # all the way until the max_cmb_len
        if not self.__count:
            self.__count = sum(
                comb(len(self.chunks), i) for i in range(1, self.max_cmb_len + 1)
            )
        return self.__count
