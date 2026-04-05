from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pet.core import encode
from tools.pathwise_first_bad_ancestor_probe import compare_builders_toward_target


@pytest.mark.parametrize(
    "start_n,target",
    [
        (36, 50),
        (36, 200),
        (36, 300),
        (144, 500),
        (144, 1300),
        (144, 5000),
    ],
)
def test_lookahead_is_never_worse_than_greedy_across_two_local_patterns(start_n, target):
    start = encode(start_n)
    report = compare_builders_toward_target(start, target=target, step_limit=5, limit=200)

    assert report["lookahead"]["final_distance"] <= report["greedy"]["final_distance"]
