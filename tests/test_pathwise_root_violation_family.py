from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pet.core import encode
from tools.pathwise_one_step_probe import apply_rw
from tools.pathwise_first_bad_ancestor_probe import (
    pathwise_ceiling_trace,
    first_violation_from_trace,
)


@pytest.mark.parametrize(
    "initial_h,path,child_idx,new_g,expected",
    [
        (36,  (1,), 0, 2, {"path": (), "index": 0, "left": 2, "right": 4}),
        (180, (1,), 0, 2, {"path": (), "index": 0, "left": 2, "right": 4}),
        (900, (1,), 0, 2, {"path": (), "index": 0, "left": 2, "right": 4}),
        (900, (2,), 0, 2, {"path": (), "index": 1, "left": 2, "right": 4}),
    ],
)
def test_known_root_failures_have_expected_first_violation(
    initial_h, path, child_idx, new_g, expected
):
    tree0 = encode(initial_h)
    tree1 = apply_rw(tree0, path, child_idx, new_g)
    trace = pathwise_ceiling_trace(tree0, tree1, path)

    assert first_violation_from_trace(trace) == expected
