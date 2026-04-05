from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pet.core import encode
from tools.pathwise_first_bad_ancestor_probe import greedy_pathwise_build_toward_target


@pytest.mark.parametrize("target", [50, 200, 300])
def test_greedy_builder_never_accepts_non_improving_steps(target):
    start = encode(36)
    result = greedy_pathwise_build_toward_target(start, target=target, step_limit=5, limit=100)

    assert all(
        step["distance_after"] < step["distance_before"]
        for step in result["history"]
    )
