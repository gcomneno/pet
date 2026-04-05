from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.pathwise_first_bad_ancestor_probe import propose_seed_family_for_target


def test_propose_seed_family_for_target_returns_unique_bounded_candidates():
    target = 200
    family = propose_seed_family_for_target(target=target, pool_limit=500, top_k=10)
    seeds = [item["seed"] for item in family]

    assert family
    assert len(family) <= 10
    assert len(seeds) == len(set(seeds))
    assert all(2 <= n <= 500 for n in seeds)


def test_propose_seed_family_for_target_reserves_both_sides_when_possible():
    target = 200
    family = propose_seed_family_for_target(target=target, pool_limit=500, top_k=10)
    seeds = [item["seed"] for item in family]

    below = [n for n in seeds if n < target]
    above = [n for n in seeds if n > target]

    assert below, family
    assert above, family


def test_propose_seed_family_for_target_stays_within_pool_limit():
    family = propose_seed_family_for_target(target=1000, pool_limit=500, top_k=20)
    seeds = [item["seed"] for item in family]

    assert all(2 <= n <= 500 for n in seeds)
