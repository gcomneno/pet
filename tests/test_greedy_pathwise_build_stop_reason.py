from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pet.core import encode
from tools.pathwise_first_bad_ancestor_probe import greedy_pathwise_build_toward_target


def test_greedy_builder_reports_no_improving_move_when_already_stuck():
    start = encode(36)
    result = greedy_pathwise_build_toward_target(start, target=36, step_limit=3, limit=100)

    assert result["history"] == []
    assert result["stop_reason"] == "no_improving_move"


def test_greedy_builder_reports_step_limit_when_budget_exhausted():
    start = encode(36)
    result = greedy_pathwise_build_toward_target(start, target=10**9, step_limit=1, limit=100)

    assert len(result["history"]) == 1
    assert result["stop_reason"] == "step_limit"
