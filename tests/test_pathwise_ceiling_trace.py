from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pet.core import encode
from tools.pathwise_one_step_probe import apply_rw
from tools.pathwise_first_bad_ancestor_probe import pathwise_ceiling_trace


def test_pathwise_ceiling_trace_for_minimal_witness():
    tree0 = encode(36)
    tree1 = apply_rw(tree0, (1,), 0, 2)

    trace = pathwise_ceiling_trace(tree0, tree1, (1,))

    assert trace == [
        {
            "path": (),
            "before": [2, 2],
            "after": [2, 4],
            "locally_canonical": False,
        },
        {
            "path": (1,),
            "before": [1],
            "after": [2],
            "locally_canonical": True,
        },
    ]
