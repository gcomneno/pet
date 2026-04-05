from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.pathwise_first_bad_ancestor_probe import choose_best_seed_toward_target


def test_choose_best_seed_toward_target_accepts_structured_seed_family_v1():
    family = [
        {
            "seed": 36,
            "source": "below",
            "source_rank": 0,
            "distance_to_target": 164,
            "priority_key": (0, 164, 36, 0),
        },
        {
            "seed": 144,
            "source": "below",
            "source_rank": 0,
            "distance_to_target": 56,
            "priority_key": (0, 56, 144, 1),
        },
    ]

    report = choose_best_seed_toward_target(
        target=200,
        seed_ns=family,
        builder="lookahead",
        step_limit=5,
        limit=100,
    )

    assert report["target"] == 200
    assert report["builder"] == "lookahead"
    assert report["best_seed"] in {36, 144}
    assert "candidates" in report
