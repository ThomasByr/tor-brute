from __future__ import annotations

import logging
import re
from itertools import combinations, permutations, product
from math import comb, perm, prod
from typing import Generator

__all__ = ["PasswdGenerator", "TupleGenerator"]


is_whitespace = re.compile(r"\s+").match


class PasswdGenerator:
    def __init__(self, filepath: str = "assets/passwd.txt", max_cmb_len=2, do_all: bool = False) -> None:
        self.__count: int = None
        self.logger = logging.getLogger(".".join(__name__.split(".")[1:]))

        self.__f = permutations if do_all else combinations
        self.__c = perm if do_all else comb

        self.max_cmb_len = max_cmb_len
        self.filepath = filepath
        with open(filepath, "r", encoding="utf-8") as f:
            self.chunks = [line.strip() for line in f if not is_whitespace(line)]

        # bellow is NOT executed if not debug
        self.logger.debug("[*] %s loaded with %d elements", filepath, self.count)

    def __iter__(self) -> Generator[str, None, None]:
        """yields all possible combinations of the chunks"""
        for i in range(1, self.max_cmb_len + 1):
            for combination in self.__f(self.chunks, i):
                yield "".join(combination)  # .lower()

    @property
    def count(self) -> int:
        """return the number of possible combinations (cached)"""
        # a, b, c will result in a, b, c, ab, ac, bc, abc
        # all the way until the max_cmb_len
        if not self.__count:
            self.__count = sum(self.__c(len(self.chunks), i) for i in range(1, self.max_cmb_len + 1))
        return self.__count


class TupleGenerator:
    def __init__(self, *generators: PasswdGenerator) -> None:
        self.generators = generators
        self.__count: int = None

        self.logger = logging.getLogger(".".join(__name__.split(".")[1:]))

        # bellow is NOT executed if not debug
        self.logger.debug(
            "[*] %s loaded with %d elements",
            self.__class__.__name__,
            self.count,
        )

    def __iter__(self) -> Generator[tuple[str, ...], None, None]:
        """yields all possible combinations of the products of the generators"""
        # consume all the generators
        # consume last one, then call one element from the previous one
        # until the first one
        # and so on ...
        # example:
        #   g1 : a, b, c
        #   g2 : d, e, f
        #   g3 : g, h, i
        #   result : (a, d, g), (a, d, h), (a, d, i), (a, e, g), (a, e, h), ...
        for combination in product(*self.generators):
            yield combination

    @property
    def count(self) -> int:
        """return the number of possible combinations (cached)"""
        if not self.__count:
            self.__count = prod(g.count for g in self.generators)
        return self.__count
