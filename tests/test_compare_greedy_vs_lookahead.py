from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pet.core import encode
from tools.pathwise_first_bad_ancestor_probe import compare_builders_toward_target


@pytest.mark.parametrize("target", [50, 200, 300, 500])
def test_lookahead_is_never_worse_than_greedy_on_final_distance(target):
    start = encode(36)
    report = compare_builders_toward_target(start, target=target, step_limit=5, limit=100)

    assert report["lookahead"]["final_distance"] <= report["greedy"]["final_distance"]


def test_compare_builders_report_has_expected_shape():
    start = encode(36)
    report = compare_builders_toward_target(start, target=200, step_limit=5, limit=100)

    assert report["target"] == 200
    assert "greedy" in report
    assert "lookahead" in report

    for key in ("start_h", "final_h", "final_distance", "step_count", "stop_reason"):
        assert key in report["greedy"]
        assert key in report["lookahead"]
