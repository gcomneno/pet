from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.pathwise_first_bad_ancestor_probe import choose_best_seed_toward_target


def test_choose_best_seed_toward_target_returns_expected_report_shape():
    report = choose_best_seed_toward_target(
        target=200,
        seed_ns=[36, 144],
        builder="lookahead",
        step_limit=5,
        limit=100,
    )

    assert report["target"] == 200
    assert report["builder"] == "lookahead"
    assert "best_seed" in report
    assert "best_result" in report
    assert "candidates" in report


def test_choose_best_seed_toward_target_picks_closest_final_result():
    report = choose_best_seed_toward_target(
        target=200,
        seed_ns=[36, 144],
        builder="lookahead",
        step_limit=5,
        limit=100,
    )

    best_distance = report["best_result"]["final_distance"]
    assert all(
        best_distance <= candidate["final_distance"]
        for candidate in report["candidates"]
    )
