from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.pathwise_first_bad_ancestor_probe import auto_build_toward_target


def test_auto_build_toward_target_accepts_policy_v2():
    report = auto_build_toward_target(
        target=200,
        pool_limit=500,
        top_k=8,
        builder="lookahead",
        step_limit=5,
        limit=100,
        policy="balanced",
    )

    assert report["target"] == 200
    assert report["selection_summary"]
    assert report["seed_family"]


def test_auto_build_toward_target_reports_policy_v2():
    report = auto_build_toward_target(
        target=200,
        pool_limit=500,
        top_k=8,
        builder="lookahead",
        step_limit=5,
        limit=100,
        policy="scale_first",
    )

    assert report["policy"] == "scale_first"
