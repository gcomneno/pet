from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pet.core import encode, decode
from tools.pathwise_one_step_probe import apply_rw
from tools.pathwise_first_bad_ancestor_probe import classify_pathwise_rewrite


@pytest.mark.parametrize(
    "initial_h,path,child_idx,new_g,expected_new_h,expected_failure_kind,expected_bad_path,expected_violation",
    [
        (
            36, (1,), 0, 2, 324,
            "root",
            (),
            {"path": (), "index": 0, "left": 2, "right": 4},
        ),
        (
            180, (1,), 0, 2, 1620,
            "root",
            (),
            {"path": (), "index": 0, "left": 2, "right": 4},
        ),
    ],
)
def test_classify_pathwise_rewrite_for_known_root_failures(
    initial_h, path, child_idx, new_g, expected_new_h,
    expected_failure_kind, expected_bad_path, expected_violation
):
    tree0 = encode(initial_h)
    tree1 = apply_rw(tree0, path, child_idx, new_g)

    info = classify_pathwise_rewrite(tree0, tree1, path)

    assert decode(tree1) == expected_new_h
    assert info["local_ok"] is True
    assert info["first_bad_path"] == expected_bad_path
    assert info["failure_kind"] == expected_failure_kind
    assert info["first_violation"] == expected_violation
