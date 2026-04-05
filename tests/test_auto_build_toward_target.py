from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.pathwise_first_bad_ancestor_probe import auto_build_toward_target


def test_auto_build_toward_target_returns_expected_report_shape():
    report = auto_build_toward_target(
        target=200,
        pool_limit=500,
        top_k=10,
        builder="lookahead",
        step_limit=5,
        limit=100,
    )

    assert report["target"] == 200
    assert report["builder"] == "lookahead"
    assert "seed_family" in report
    assert "best_seed" in report
    assert "best_result" in report
    assert "candidates" in report


def test_auto_build_toward_target_best_seed_belongs_to_seed_family():
    report = auto_build_toward_target(
        target=200,
        pool_limit=500,
        top_k=10,
        builder="lookahead",
        step_limit=5,
        limit=100,
    )

    assert report["best_seed"] in report["seed_family"]


def test_auto_build_toward_target_best_result_is_best_among_candidates():
    report = auto_build_toward_target(
        target=200,
        pool_limit=500,
        top_k=10,
        builder="lookahead",
        step_limit=5,
        limit=100,
    )

    best_distance = report["best_result"]["final_distance"]
    assert all(
        best_distance <= candidate["final_distance"]
        for candidate in report["candidates"]
    )
