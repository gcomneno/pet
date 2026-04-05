from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.pathwise_first_bad_ancestor_probe import propose_seed_family_for_target


def test_scale_first_policy_reserves_more_scale_anchors_than_balanced_v3():
    balanced = propose_seed_family_for_target(
        target=200,
        pool_limit=500,
        top_k=8,
        policy="balanced",
    )
    scale_first = propose_seed_family_for_target(
        target=200,
        pool_limit=500,
        top_k=8,
        policy="scale_first",
    )

    balanced_scale = [item for item in balanced if item["source"] == "scale_anchor"]
    scale_first_scale = [item for item in scale_first if item["source"] == "scale_anchor"]

    assert len(balanced_scale) == 1, balanced
    assert len(scale_first_scale) >= 2, scale_first
