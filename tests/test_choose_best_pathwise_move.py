from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pet.core import encode, validate
from tools.pathwise_first_bad_ancestor_probe import choose_best_pathwise_move


def test_choose_best_pathwise_move_returns_local_ok_ranked_move_on_36():
    tree0 = encode(36)
    best = choose_best_pathwise_move(tree0, limit=100)

    assert best is not None
    assert best["new_g"] > best["old_g"]
    assert best["info"]["local_ok"] is True
    assert best["score"] is not None


def test_choose_best_pathwise_move_returns_local_ok_ranked_move_on_embedded_tree():
    tree0 = [
        (2, encode(324)),
        (3, encode(36)),
        (5, None),
    ]
    validate(tree0)

    best = choose_best_pathwise_move(tree0, limit=400)

    assert best is not None
    assert best["new_g"] > best["old_g"]
    assert best["info"]["local_ok"] is True
    assert best["score"] is not None
