from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.pathwise_first_bad_ancestor_probe import auto_build_toward_target


def test_auto_build_toward_target_candidates_are_sorted_by_final_quality_then_seed_priority_v1():
    report = auto_build_toward_target(
        target=200,
        pool_limit=500,
        top_k=10,
        builder="lookahead",
        step_limit=5,
        limit=100,
    )

    keys = [
        (
            item["final_distance"],
            item["seed_priority_key"],
        )
        for item in report["candidates"]
    ]

    assert keys == sorted(keys), report["candidates"]
