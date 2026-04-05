from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pet.core import encode
from tools.pathwise_first_bad_ancestor_probe import (
    choose_best_two_step_pathwise_move_toward_target,
    lookahead_pathwise_build_toward_target,
)


def test_lookahead_builder_uses_first_move_of_two_step_plan():
    start = encode(36)
    target = 200

    plan = choose_best_two_step_pathwise_move_toward_target(start, target=target, limit=100)
    result = lookahead_pathwise_build_toward_target(start, target=target, step_limit=1, limit=100)

    assert plan is not None
    assert result["history"]
    assert result["history"][0]["path"] == plan["first_move"]["path"]
    assert result["history"][0]["child_idx"] == plan["first_move"]["child_idx"]
    assert result["history"][0]["new_g"] == plan["first_move"]["new_g"]


def test_lookahead_builder_never_accepts_non_improving_steps():
    start = encode(36)
    result = lookahead_pathwise_build_toward_target(start, target=200, step_limit=5, limit=100)

    assert all(
        step["distance_after"] < step["distance_before"]
        for step in result["history"]
    )
