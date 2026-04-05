from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.pathwise_first_bad_ancestor_probe import auto_build_toward_target


def test_auto_build_toward_target_reports_selection_summary():
    report = auto_build_toward_target(
        target=200,
        pool_limit=500,
        top_k=10,
        builder="lookahead",
        step_limit=5,
        limit=100,
    )

    assert "selection_summary" in report

    summary = report["selection_summary"]
    assert summary["best_seed"] == report["best_seed"]
    assert summary["best_seed_source"] == report["best_seed_entry"]["source"]
    assert summary["initial_distance"] == report["best_result"]["initial_distance"]
    assert summary["final_distance"] == report["best_result"]["final_distance"]
    assert summary["improvement"] == (
        report["best_result"]["initial_distance"] - report["best_result"]["final_distance"]
    )
