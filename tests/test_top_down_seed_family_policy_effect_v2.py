from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.pathwise_first_bad_ancestor_probe import propose_seed_family_for_target


def test_scale_first_policy_prioritizes_scale_anchor_over_above_v2():
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

    balanced_sources = [item["source"] for item in balanced]
    scale_first_sources = [item["source"] for item in scale_first]

    assert balanced_sources.index("above") < balanced_sources.index("scale_anchor")
    assert scale_first_sources.index("scale_anchor") < scale_first_sources.index("above")
