from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.pathwise_first_bad_ancestor_probe import auto_build_toward_target


def test_auto_build_toward_target_exposes_second_scale_anchor_v3():
    balanced = auto_build_toward_target(
        target=200,
        pool_limit=500,
        top_k=8,
        builder="lookahead",
        step_limit=5,
        limit=100,
        policy="balanced",
    )
    scale_first = auto_build_toward_target(
        target=200,
        pool_limit=500,
        top_k=8,
        builder="lookahead",
        step_limit=5,
        limit=100,
        policy="scale_first",
    )

    balanced_scale = [
        item["seed"] for item in balanced["seed_family"] if item["source"] == "scale_anchor"
    ]
    scale_first_scale = [
        item["seed"] for item in scale_first["seed_family"] if item["source"] == "scale_anchor"
    ]

    assert len(balanced_scale) == 1, balanced["seed_family"]
    assert len(scale_first_scale) >= 2, scale_first["seed_family"]

    chooser_scale = {
        item["seed_n"] for item in scale_first["candidates"] if item["seed_source"] == "scale_anchor"
    }

    assert set(scale_first_scale[:2]).issubset(chooser_scale), scale_first["candidates"]
