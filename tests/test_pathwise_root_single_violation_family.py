from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pet.core import encode
from tools.pathwise_one_step_probe import apply_rw
from tools.pathwise_first_bad_ancestor_probe import (
    classify_pathwise_rewrite,
    local_ceiling_violations,
)


@pytest.mark.parametrize(
    "initial_h,path,child_idx,new_g",
    [
        (36,  (1,), 0, 2),
        (180, (1,), 0, 2),
        (900, (1,), 0, 2),
        (900, (2,), 0, 2),
    ],
)
def test_known_root_failures_have_single_root_local_violation(
    initial_h, path, child_idx, new_g
):
    tree0 = encode(initial_h)
    tree1 = apply_rw(tree0, path, child_idx, new_g)

    info = classify_pathwise_rewrite(tree0, tree1, path)
    root_violations = local_ceiling_violations(info["trace"][0]["after"])

    assert info["failure_kind"] == "root"
    assert info["first_bad_path"] == ()
    assert len(root_violations) == 1
    assert root_violations[0] == {
        "index": info["first_violation"]["index"],
        "left": info["first_violation"]["left"],
        "right": info["first_violation"]["right"],
    }
