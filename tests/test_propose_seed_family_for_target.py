from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.pathwise_first_bad_ancestor_probe import propose_seed_family_for_target


def test_propose_seed_family_for_target_returns_sorted_unique_candidates():
    seeds = propose_seed_family_for_target(target=200, pool_limit=500, top_k=10)

    assert seeds
    assert len(seeds) <= 10
    assert len(seeds) == len(set(seeds))
    assert seeds == sorted(seeds, key=lambda n: abs(n - 200))


def test_propose_seed_family_for_target_stays_within_pool_limit():
    seeds = propose_seed_family_for_target(target=1000, pool_limit=500, top_k=20)

    assert all(2 <= n <= 500 for n in seeds)
