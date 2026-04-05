from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.pathwise_first_bad_ancestor_probe import auto_build_toward_target


def test_scale_first_prefers_constructive_scale_anchor_on_final_distance_tie_v4():
    report = auto_build_toward_target(
        target=432,
        pool_limit=500,
        top_k=8,
        builder="lookahead",
        step_limit=5,
        limit=100,
        policy="scale_first",
    )

    constructive = next(
        item for item in report["candidates"]
        if item["seed_n"] == 210 and item["seed_source"] == "scale_anchor"
    )
    static = next(
        item for item in report["candidates"]
        if item["seed_n"] == 420 and item["seed_source"] == "below"
    )

    assert constructive["final_distance"] == static["final_distance"] == 12
    assert constructive["step_count"] > 0
    assert static["step_count"] == 0

    assert report["best_result"]["seed_n"] == constructive["seed_n"]
    assert report["best_result"]["seed_source"] == "scale_anchor"
    assert report["best_result"]["step_count"] > 0
