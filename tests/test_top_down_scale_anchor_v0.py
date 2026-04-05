from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.pathwise_first_bad_ancestor_probe import propose_seed_family_for_target


def test_propose_seed_family_for_target_reports_seed_sources():
    family = propose_seed_family_for_target(target=200, pool_limit=500, top_k=6)

    assert family
    assert all(isinstance(item, dict) for item in family), family
    assert all("seed" in item and "source" in item for item in family), family
    assert {item["source"] for item in family} >= {"below", "above", "scale_anchor"}, family
