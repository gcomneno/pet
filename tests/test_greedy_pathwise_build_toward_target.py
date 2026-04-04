from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pet.core import encode
from tools.pathwise_first_bad_ancestor_probe import greedy_pathwise_build_toward_target


def test_greedy_builder_toward_200_from_36_starts_with_144():
    start = encode(36)
    result = greedy_pathwise_build_toward_target(start, target=200, step_limit=3, limit=100)

    assert result["history"]
    assert result["history"][0]["new_h"] == 144


def test_greedy_builder_monotonically_improves_or_stops():
    start = encode(36)
    result = greedy_pathwise_build_toward_target(start, target=200, step_limit=5, limit=100)

    assert all(
        step["distance_after"] < step["distance_before"]
        for step in result["history"]
    )
