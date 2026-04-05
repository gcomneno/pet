from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.pathwise_first_bad_ancestor_probe import propose_seed_family_for_target


def test_propose_seed_family_for_target_reports_priority_fields_v1():
    family = propose_seed_family_for_target(target=200, pool_limit=500, top_k=8)

    assert family
    assert all("seed" in item for item in family)
    assert all("source" in item for item in family)
    assert all("source_rank" in item for item in family)
    assert all("distance_to_target" in item for item in family)
    assert all("priority_key" in item for item in family)


def test_propose_seed_family_for_target_is_sorted_by_priority_key_v1():
    family = propose_seed_family_for_target(target=200, pool_limit=500, top_k=8)
    keys = [item["priority_key"] for item in family]

    assert keys == sorted(keys), family
