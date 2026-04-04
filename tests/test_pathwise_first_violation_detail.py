from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pet.core import encode
from tools.pathwise_one_step_probe import apply_rw
from tools.pathwise_first_bad_ancestor_probe import (
    pathwise_ceiling_trace,
    first_violation_from_trace,
)


def test_first_violation_from_trace_for_minimal_witness():
    tree0 = encode(36)
    tree1 = apply_rw(tree0, (1,), 0, 2)

    trace = pathwise_ceiling_trace(tree0, tree1, (1,))

    assert first_violation_from_trace(trace) == {
        "path": (),
        "index": 0,
        "left": 2,
        "right": 4,
    }
