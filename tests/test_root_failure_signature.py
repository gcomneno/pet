from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pet.core import encode
from tools.pathwise_one_step_probe import apply_rw
from tools.pathwise_first_bad_ancestor_probe import root_failure_signature


@pytest.mark.parametrize(
    "initial_h,path,child_idx,new_g,expected",
    [
        (
            36, (1,), 0, 2,
            {
                "local_ok": True,
                "first_bad_path": (),
                "violation_count_at_bad_path": 1,
                "first_violation": {"path": (), "index": 0, "left": 2, "right": 4},
            },
        ),
        (
            900, (2,), 0, 2,
            {
                "local_ok": True,
                "first_bad_path": (),
                "violation_count_at_bad_path": 1,
                "first_violation": {"path": (), "index": 1, "left": 2, "right": 4},
            },
        ),
    ],
)
def test_root_failure_signature_for_known_witnesses(
    initial_h, path, child_idx, new_g, expected
):
    tree0 = encode(initial_h)
    tree1 = apply_rw(tree0, path, child_idx, new_g)

    assert root_failure_signature(tree0, tree1, path) == expected
