from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.pathwise_first_bad_ancestor_probe import auto_build_toward_target


def test_auto_build_toward_target_candidates_include_top_down_seed_metadata():
    report = auto_build_toward_target(
        target=200,
        pool_limit=500,
        top_k=10,
        builder="lookahead",
        step_limit=5,
        limit=100,
    )

    assert report["candidates"]
    assert all("seed_source" in item for item in report["candidates"])
    assert all("initial_distance" in item for item in report["candidates"])
    assert all("final_distance" in item for item in report["candidates"])
