from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.pathwise_first_bad_ancestor_probe import (
    propose_seed_family_for_target,
    choose_best_seed_toward_target,
)


def test_scale_first_policy_exposes_second_scale_anchor_to_chooser_v3():
    balanced_family = propose_seed_family_for_target(
        target=200,
        pool_limit=500,
        top_k=8,
        policy="balanced",
    )
    scale_first_family = propose_seed_family_for_target(
        target=200,
        pool_limit=500,
        top_k=8,
        policy="scale_first",
    )

    balanced_scale = [item["seed"] for item in balanced_family if item["source"] == "scale_anchor"]
    scale_first_scale = [item["seed"] for item in scale_first_family if item["source"] == "scale_anchor"]

    assert len(balanced_scale) == 1, balanced_family
    assert len(scale_first_scale) >= 2, scale_first_family

    report = choose_best_seed_toward_target(
        target=200,
        seed_ns=scale_first_family,
        builder="lookahead",
        step_limit=5,
        limit=100,
        policy="scale_first",
    )

    chooser_scale = {item["seed_n"] for item in report["candidates"] if item["seed_source"] == "scale_anchor"}

    assert set(scale_first_scale[:2]).issubset(chooser_scale), report["candidates"]
