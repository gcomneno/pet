from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.pathwise_first_bad_ancestor_probe import propose_seed_family_for_target


def test_propose_seed_family_for_target_reserves_slots_on_both_sides_for_skew_target():
    target = 72
    seeds = propose_seed_family_for_target(target=target, pool_limit=500, top_k=6)

    below = [n for n in seeds if n < target]
    above = [n for n in seeds if n > target]

    assert len(seeds) == 6, seeds
    assert len(below) >= 2, seeds
    assert len(above) >= 2, seeds
