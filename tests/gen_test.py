import os
from math import comb, perm, prod
from src.generator import PasswdGenerator, TupleGenerator


cwd = os.getcwd()
file_path = os.path.join(cwd, "tmp.txt")
file_content = """
foo
bar
baz
test
admin
"""


def setup_module(_):
    """setup any state specific to the execution of the given module."""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(file_content)


def teardown_module(_):
    """teardown any state that was previously setup with a setup_module
    method.
    """
    os.unlink(file_path)


def test_basic():
    g0 = PasswdGenerator(file_path, 2)
    g1 = PasswdGenerator(file_path, 2, True)

    assert g0.count == 21
    assert g1.count == 36

    assert len(list(g0)) == 21
    assert len(list(g1)) == 36


def test_length():
    for i in range(n := len(file_content.splitlines())):
        g0 = PasswdGenerator(file_path, i)
        g1 = PasswdGenerator(file_path, i, True)

        assert g0.count == sum(comb(n, j) for j in range(1, i + 1))
        assert g1.count == sum(perm(n, j) for j in range(1, i + 1))

        assert len(list(g0)) == g0.count
        assert len(list(g1)) == g1.count


def test_tuple():
    generators = []
    n = len(file_content.splitlines())
    m = 3  #! KEEP LOW
    p = 2  #! KEEP LOW
    for i in range(m):
        generators.append(PasswdGenerator(file_path, p, True))
        g = TupleGenerator(*generators)
        assert g.count == prod(sum(perm(n, j) for j in range(1, p + 1)) for _ in range(i + 1))
        assert g.count == prod(__g.count for __g in generators)
        assert len(list(g)) == g.count
