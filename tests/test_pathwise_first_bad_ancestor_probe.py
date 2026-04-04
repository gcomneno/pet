from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pet.core import encode, decode
from tools.pathwise_one_step_probe import apply_rw, get_subtree, is_locally_canonical
from tools.pathwise_first_bad_ancestor_probe import first_bad_ancestor
from tools.prune_absorption_check import child_generators


def test_first_bad_ancestor_is_root_for_minimal_pathwise_witness():
    tree0 = encode(36)
    tree1 = apply_rw(tree0, (1,), 0, 2)

    local1 = get_subtree(tree1, (1,))
    bad_path, bad_gs = first_bad_ancestor(tree1, (1,))

    assert decode(tree1) == 324
    assert is_locally_canonical(local1) is True
    assert bad_path == ()
    assert child_generators(tree0) == [2, 2]
    assert child_generators(tree1) == [2, 4]
    assert bad_gs == [2, 4]
