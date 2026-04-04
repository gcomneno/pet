from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pet.core import encode, validate
from tools.pathwise_one_step_probe import apply_rw
from tools.pathwise_first_bad_ancestor_probe import classify_pathwise_rewrite
from tools.prune_absorption_check import child_generators
from tools.forest_rewrite_check import get_subtree


def test_embedded_ancestor_witness_with_explicit_canonical_embedding():
    tree0 = [
        (2, encode(324)),
        (3, encode(36)),
        (5, None),
    ]
    validate(tree0)

    tree1 = apply_rw(tree0, (1, 1), 0, 2)
    validate(tree1)

    info = classify_pathwise_rewrite(tree0, tree1, (1, 1))

    assert child_generators(tree0) == [324, 36, 1]
    assert child_generators(tree1) == [324, 324, 1]
    assert child_generators(get_subtree(tree0, (1,))) == [2, 2]
    assert child_generators(get_subtree(tree1, (1,))) == [2, 4]

    assert info["local_ok"] is True
    assert info["failure_kind"] == "embedded_ancestor"
    assert info["first_bad_path"] == (1,)
    assert info["first_violation"] == {
        "path": (1,),
        "index": 0,
        "left": 2,
        "right": 4,
    }
