from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pet.core import encode, decode
from tools.pathwise_one_step_probe import apply_rw, get_subtree, is_locally_canonical
from tools.pathwise_first_bad_ancestor_probe import classify_pathwise_rewrite
from tools.prune_absorption_check import child_generators


def test_second_local_pattern_has_clean_safe_step_at_144():
    tree0 = encode(144)
    tree1 = apply_rw(tree0, (1,), 0, 2)

    info = classify_pathwise_rewrite(tree0, tree1, (1,))

    assert decode(tree1) == 1296
    assert child_generators(tree0) == [4, 2]
    assert child_generators(tree1) == [4, 4]
    assert child_generators(get_subtree(tree0, (1,))) == [1]
    assert child_generators(get_subtree(tree1, (1,))) == [2]
    assert is_locally_canonical(get_subtree(tree1, (1,))) is True
    assert info["failure_kind"] is None
    assert info["first_bad_path"] is None
    assert info["first_violation"] is None


def test_second_local_pattern_overgrows_at_1296():
    tree0 = encode(1296)
    tree1 = apply_rw(tree0, (1,), 0, 4)

    info = classify_pathwise_rewrite(tree0, tree1, (1,))

    assert child_generators(tree0) == [4, 4]
    assert child_generators(tree1) == [4, 16]
    assert is_locally_canonical(get_subtree(tree1, (1,))) is True
    assert info["failure_kind"] == "root"
    assert info["first_bad_path"] == ()
    assert info["first_violation"] == {
        "path": (),
        "index": 0,
        "left": 4,
        "right": 16,
    }
