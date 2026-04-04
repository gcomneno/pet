from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pet.core import encode, validate
from tools.pathwise_one_step_probe import apply_rw
from tools.pathwise_first_bad_ancestor_probe import classify_pathwise_rewrite


@pytest.mark.parametrize(
    "kind,tree0,path,child_idx,new_g,expected_failure_kind,expected_bad_path,expected_violation",
    [
        (
            "root",
            encode(36),
            (1,),
            0,
            2,
            "root",
            (),
            {"path": (), "index": 0, "left": 2, "right": 4},
        ),
        (
            "embedded",
            [(2, encode(324)), (3, encode(36)), (5, None)],
            (1, 1),
            0,
            2,
            "embedded_ancestor",
            (1,),
            {"path": (1,), "index": 0, "left": 2, "right": 4},
        ),
    ],
)
def test_absorption_controls_failure_location(
    kind, tree0, path, child_idx, new_g,
    expected_failure_kind, expected_bad_path, expected_violation
):
    if kind == "embedded":
        validate(tree0)

    tree1 = apply_rw(tree0, path, child_idx, new_g)
    if kind == "embedded":
        validate(tree1)

    info = classify_pathwise_rewrite(tree0, tree1, path)

    assert info["local_ok"] is True
    assert info["failure_kind"] == expected_failure_kind
    assert info["first_bad_path"] == expected_bad_path
    assert info["first_violation"] == expected_violation
