from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pet.core import encode, decode
from tools.pathwise_one_step_probe import apply_rw
from tools.pathwise_first_bad_ancestor_probe import classify_pathwise_rewrite


@pytest.mark.parametrize(
    "initial_h,path,child_idx,new_g,expected_new_h",
    [
        (36,  (1,), 0, 2, 324),
        (180, (1,), 0, 2, 1620),
        (900, (1,), 0, 2, 8100),
        (900, (2,), 0, 2, 22500),
    ],
)
def test_known_root_failures_share_same_classification_signature(
    initial_h, path, child_idx, new_g, expected_new_h
):
    tree0 = encode(initial_h)
    tree1 = apply_rw(tree0, path, child_idx, new_g)

    info = classify_pathwise_rewrite(tree0, tree1, path)

    assert decode(tree1) == expected_new_h
    assert info["local_ok"] is True
    assert info["failure_kind"] == "root"
    assert info["first_bad_path"] == ()
    assert info["first_violation"] is not None
    assert info["first_violation"]["path"] == ()
