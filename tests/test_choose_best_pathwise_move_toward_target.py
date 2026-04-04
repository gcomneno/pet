from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pet.core import encode
from tools.pathwise_first_bad_ancestor_probe import choose_best_pathwise_move_toward_target


def test_choose_best_move_toward_target_prefers_closer_move_on_36():
    tree0 = encode(36)

    # candidate moves known from current ranking:
    # 36 -> 144  via root move
    # 36 -> 324  via embedded/root-failure witness move
    # for target 200, 144 is closer than 324
    best = choose_best_pathwise_move_toward_target(tree0, target=200, limit=100)

    assert best is not None
    assert best["new_h"] == 144


def test_choose_best_move_toward_target_can_pick_324_when_target_is_higher():
    tree0 = encode(36)

    # for target 300, 324 is closer than 144
    best = choose_best_pathwise_move_toward_target(tree0, target=300, limit=100)

    assert best is not None
    assert best["new_h"] == 324
