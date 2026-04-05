from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.pathwise_first_bad_ancestor_probe import auto_build_toward_target


def test_auto_build_toward_target_selection_summary_matches_best_result_v1():
    report = auto_build_toward_target(
        target=200,
        pool_limit=500,
        top_k=10,
        builder="lookahead",
        step_limit=5,
        limit=100,
    )

    summary = report["selection_summary"]
    best = report["best_result"]
    best_entry = report["best_seed_entry"]

    assert summary["best_seed"] == report["best_seed"] == best["seed_n"]
    assert summary["best_seed_source"] == best_entry["source"] == best["seed_source"]
    assert summary["best_seed_priority_key"] == best_entry["priority_key"] == best["seed_priority_key"]
    assert summary["initial_distance"] == best["initial_distance"]
    assert summary["final_distance"] == best["final_distance"]
    assert summary["improvement"] == best["initial_distance"] - best["final_distance"]
