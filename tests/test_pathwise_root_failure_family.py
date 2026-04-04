from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pet.core import encode, decode
from tools.pathwise_one_step_probe import apply_rw, get_subtree, is_locally_canonical
from tools.pathwise_first_bad_ancestor_probe import (
    pathwise_ceiling_trace,
    first_bad_path_from_trace,
    first_violation_from_trace,
)


@pytest.mark.parametrize(
    "initial_h,path,child_idx,new_g,expected_new_h",
    [
        (36,   (1,), 0, 2, 324),
        (180,  (1,), 0, 2, 1620),
        (900,  (1,), 0, 2, 8100),
        (900,  (2,), 0, 2, 22500),
    ],
)
def test_known_root_failures_have_root_as_first_bad_path(
    initial_h, path, child_idx, new_g, expected_new_h
):
    tree0 = encode(initial_h)
    tree1 = apply_rw(tree0, path, child_idx, new_g)

    local1 = get_subtree(tree1, path)
    trace = pathwise_ceiling_trace(tree0, tree1, path)
    first_bad = first_bad_path_from_trace(trace)
    first_violation = first_violation_from_trace(trace)

    assert decode(tree1) == expected_new_h
    assert is_locally_canonical(local1) is True
    assert first_bad == ()
    assert first_violation is not None
    assert first_violation["path"] == ()
