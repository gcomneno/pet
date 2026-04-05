from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pet.core import encode
from tools.pathwise_first_bad_ancestor_probe import (
    choose_best_pathwise_move_toward_target,
    choose_best_two_step_pathwise_move_toward_target,
)


def test_two_step_chooser_is_never_worse_than_one_step_on_final_distance():
    tree0 = encode(36)
    target = 200

    one = choose_best_pathwise_move_toward_target(tree0, target=target, limit=100)
    two = choose_best_two_step_pathwise_move_toward_target(tree0, target=target, limit=100)

    assert one is not None
    assert two is not None

    assert abs(two["final_h"] - target) <= abs(one["new_h"] - target)


def test_two_step_chooser_returns_first_move_and_plan_summary():
    tree0 = encode(36)
    target = 300

    plan = choose_best_two_step_pathwise_move_toward_target(tree0, target=target, limit=100)

    assert plan is not None
    assert "first_move" in plan
    assert "final_h" in plan
    assert "steps" in plan
    assert len(plan["steps"]) in (1, 2)
