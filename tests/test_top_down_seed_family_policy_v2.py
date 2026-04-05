from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.pathwise_first_bad_ancestor_probe import propose_seed_family_for_target


def test_propose_seed_family_for_target_accepts_policy_v2():
    family = propose_seed_family_for_target(
        target=200,
        pool_limit=500,
        top_k=8,
        policy="balanced",
    )

    assert family
    assert all("priority_key" in item for item in family)


def test_propose_seed_family_for_target_scale_first_policy_prioritizes_scale_anchor_v2():
    family = propose_seed_family_for_target(
        target=200,
        pool_limit=500,
        top_k=8,
        policy="scale_first",
    )

    sources = [item["source"] for item in family]
    first_scale = sources.index("scale_anchor")
    first_fill = sources.index("fill") if "fill" in sources else len(sources)

    assert first_scale < first_fill, family
