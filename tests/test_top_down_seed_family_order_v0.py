from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.pathwise_first_bad_ancestor_probe import propose_seed_family_for_target


def test_propose_seed_family_for_target_orders_sources_by_priority():
    family = propose_seed_family_for_target(target=200, pool_limit=500, top_k=8)
    sources = [item["source"] for item in family]

    first_fill = next((i for i, s in enumerate(sources) if s == "fill"), len(sources))
    first_scale = next((i for i, s in enumerate(sources) if s == "scale_anchor"), len(sources))
    first_above = next((i for i, s in enumerate(sources) if s == "above"), len(sources))
    first_below = next((i for i, s in enumerate(sources) if s == "below"), len(sources))

    assert first_below < first_above, sources
    assert first_above < first_scale, sources
    assert first_scale < first_fill, sources
