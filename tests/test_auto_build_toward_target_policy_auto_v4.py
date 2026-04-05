from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.pathwise_first_bad_ancestor_probe import auto_build_toward_target


def test_auto_build_toward_target_resolves_scale_first_when_constructive_anchor_is_competitive_v4():
    report = auto_build_toward_target(
        target=432,
        pool_limit=500,
        top_k=8,
        builder="lookahead",
        step_limit=5,
        limit=100,
        policy="auto",
    )

    assert report["policy"] == "auto"
    assert report["resolved_policy"] == "scale_first"
    assert report["best_result"]["seed_source"] == "scale_anchor"
    assert report["best_result"]["step_count"] > 0


def test_auto_build_toward_target_resolves_balanced_when_no_competitive_constructive_anchor_exists_v4():
    report = auto_build_toward_target(
        target=200,
        pool_limit=500,
        top_k=8,
        builder="lookahead",
        step_limit=5,
        limit=100,
        policy="auto",
    )

    assert report["policy"] == "auto"
    assert report["resolved_policy"] == "balanced"
    assert report["best_result"]["seed_source"] == "below"
