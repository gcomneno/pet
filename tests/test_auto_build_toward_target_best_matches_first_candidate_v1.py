from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.pathwise_first_bad_ancestor_probe import auto_build_toward_target


def test_auto_build_toward_target_best_result_matches_first_sorted_candidate_v1():
    report = auto_build_toward_target(
        target=200,
        pool_limit=500,
        top_k=10,
        builder="lookahead",
        step_limit=5,
        limit=100,
    )

    first = report["candidates"][0]
    best = report["best_result"]

    assert best["seed_n"] == first["seed_n"]
    assert best["final_distance"] == first["final_distance"]
    assert best["seed_source"] == first["seed_source"]
    assert report["best_seed"] == first["seed_n"]
