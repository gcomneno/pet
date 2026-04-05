from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.pathwise_first_bad_ancestor_probe import propose_seed_family_for_target


def test_scale_first_policy_places_both_scale_anchors_before_fill_v3():
    family = propose_seed_family_for_target(
        target=200,
        pool_limit=500,
        top_k=8,
        policy="scale_first",
    )

    sources = [item["source"] for item in family]
    scale_positions = [i for i, source in enumerate(sources) if source == "scale_anchor"]
    fill_positions = [i for i, source in enumerate(sources) if source == "fill"]

    assert len(scale_positions) >= 2, family
    assert fill_positions, family
    assert max(scale_positions[:2]) < min(fill_positions), family
