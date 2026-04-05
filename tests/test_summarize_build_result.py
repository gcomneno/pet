from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pet.core import encode
from tools.pathwise_first_bad_ancestor_probe import (
    greedy_pathwise_build_toward_target,
    summarize_build_result,
)


def test_summarize_build_result_has_expected_top_level_fields():
    start = encode(36)
    result = greedy_pathwise_build_toward_target(start, target=200, step_limit=3, limit=100)
    summary = summarize_build_result(result)

    for key in (
        "start_h",
        "target",
        "final_h",
        "initial_distance",
        "final_distance",
        "step_count",
        "stop_reason",
        "steps",
    ):
        assert key in summary


def test_summarize_build_result_steps_are_compact():
    start = encode(36)
    result = greedy_pathwise_build_toward_target(start, target=200, step_limit=3, limit=100)
    summary = summarize_build_result(result)

    for step in summary["steps"]:
        for key in (
            "path",
            "child_idx",
            "old_g",
            "new_g",
            "new_h",
            "distance_before",
            "distance_after",
        ):
            assert key in step
