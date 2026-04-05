from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.pathwise_first_bad_ancestor_probe import auto_build_toward_target


def test_auto_build_toward_target_reports_priority_metadata_v1():
    report = auto_build_toward_target(
        target=200,
        pool_limit=500,
        top_k=10,
        builder="lookahead",
        step_limit=5,
        limit=100,
    )

    assert "priority_key" in report["best_seed_entry"]
    assert "source_rank" in report["best_seed_entry"]
    assert "distance_to_target" in report["best_seed_entry"]

    assert "best_seed_priority_key" in report["selection_summary"]
    assert report["selection_summary"]["best_seed_priority_key"] == report["best_seed_entry"]["priority_key"]
