from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.pathwise_first_bad_ancestor_probe import auto_build_toward_target


def has_competitive_constructive_scale_anchor(target):
    report = auto_build_toward_target(
        target=target,
        pool_limit=500,
        top_k=8,
        builder="lookahead",
        step_limit=5,
        limit=100,
        policy="scale_first",
    )
    candidates = report["candidates"]
    best_static_final = min(
        item["final_distance"]
        for item in candidates
        if item["step_count"] == 0
    )
    return any(
        item["seed_source"] == "scale_anchor"
        and item["step_count"] > 0
        and (item["initial_distance"] - item["final_distance"]) > 0
        and item["final_distance"] <= best_static_final
        for item in candidates
    )


def test_scale_first_activation_law_candidate_v4():
    assert has_competitive_constructive_scale_anchor(108)
    assert has_competitive_constructive_scale_anchor(432)

    assert not has_competitive_constructive_scale_anchor(200)
    assert not has_competitive_constructive_scale_anchor(324)
