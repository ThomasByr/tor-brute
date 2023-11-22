import os
from math import comb, perm, prod
from src.generator import PasswdGenerator, TupleGenerator


cwd = os.getcwd()
file_path = os.path.join(cwd, "tmp.txt")

# file content keeps "\n" so either use strip() when counting or begin right after """
# file_content = Literal['\nfoo\nbar\nbaz\ntest\nadmin\n']
# strip would remove the first and last "\n" so that it does not generate empty strings
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

    assert g0.count == 15  # 5C2 + 5
    assert g1.count == 25  # 5P2 + 5

    assert len(list(g0)) == 15
    assert len(list(g1)) == 25


def test_length():
    for i in range(n := len(file_content.strip().splitlines())):
        g0 = PasswdGenerator(file_path, i)
        g1 = PasswdGenerator(file_path, i, True)

        assert g0.count == sum(comb(n, j) for j in range(1, i + 1))
        assert g1.count == sum(perm(n, j) for j in range(1, i + 1))

        assert len(list(g0)) == g0.count
        assert len(list(g1)) == g1.count


def test_tuple():
    generators = []
    n = len(file_content.strip().splitlines())
    m = 3  #! KEEP LOW
    p = 2  #! KEEP LOW
    for i in range(m):
        generators.append(PasswdGenerator(file_path, p, True))
        g = TupleGenerator(*generators)
        assert g.count == prod(sum(perm(n, j) for j in range(1, p + 1)) for _ in range(i + 1))
        assert g.count == prod(__g.count for __g in generators)
        assert len(list(g)) == g.count
