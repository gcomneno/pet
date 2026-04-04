from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pet.core import encode, decode
from tools.pathwise_one_step_probe import (
    get_subtree,
    apply_rw,
    child_generators,
    is_locally_canonical,
    is_globally_canonical,
)


def test_one_step_rewrite_can_be_local_ok_but_global_fail():
    tree0 = encode(36)
    tree1 = apply_rw(tree0, (1,), 0, 2)

    local0 = get_subtree(tree0, (1,))
    local1 = get_subtree(tree1, (1,))

    assert decode(tree1) == 324
    assert child_generators(tree0) == [2, 2]
    assert child_generators(tree1) == [2, 4]
    assert child_generators(local0) == [1]
    assert child_generators(local1) == [2]
    assert is_locally_canonical(local1) is True
    assert is_globally_canonical(tree1) is False
