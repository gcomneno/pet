from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.pathwise_first_bad_ancestor_probe import auto_build_toward_target


def test_auto_build_toward_target_best_result_includes_seed_source():
    report = auto_build_toward_target(
        target=200,
        pool_limit=500,
        top_k=10,
        builder="lookahead",
        step_limit=5,
        limit=100,
    )

    assert report["best_result"]["seed_n"] == report["best_seed"]
    assert report["best_result"]["seed_source"] == report["best_seed_entry"]["source"]
