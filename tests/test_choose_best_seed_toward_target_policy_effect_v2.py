from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.pathwise_first_bad_ancestor_probe import choose_best_seed_toward_target


def test_choose_best_seed_toward_target_scale_first_breaks_real_tie_in_favor_of_scale_anchor_v2():
    family = [
        {
            "seed": 192,
            "source": "below",
            "source_rank": 0,
            "distance_to_target": 8,
            "priority_key": (0, 8, 192, 0),
        },
        {
            "seed": 48,
            "source": "scale_anchor",
            "source_rank": 1,
            "distance_to_target": 152,
            "priority_key": (1, 152, 48, 1),
        },
    ]

    balanced = choose_best_seed_toward_target(
        target=200,
        seed_ns=family,
        builder="lookahead",
        step_limit=5,
        limit=100,
        policy="balanced",
    )
    scale_first = choose_best_seed_toward_target(
        target=200,
        seed_ns=family,
        builder="lookahead",
        step_limit=5,
        limit=100,
        policy="scale_first",
    )

    assert balanced["best_seed"] == 192
    assert scale_first["best_seed"] == 48
