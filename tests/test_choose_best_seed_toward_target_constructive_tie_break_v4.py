from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import tools.pathwise_first_bad_ancestor_probe as probe


def test_choose_best_seed_prefers_constructive_candidate_on_true_tie_v4(monkeypatch):
    def fake_encode(seed_n):
        return seed_n

    def fake_lookahead(tree0, target, step_limit=5, limit=2000):
        if tree0 == 100:
            return {
                "start_h": 100,
                "target": target,
                "final_h": 90,
                "history": [],
                "stop_reason": "no_improving_move",
            }
        if tree0 == 101:
            return {
                "start_h": 101,
                "target": target,
                "final_h": 90,
                "history": [
                    {
                        "path": (),
                        "child_idx": 0,
                        "old_g": 1,
                        "new_g": 2,
                        "new_h": 90,
                        "distance_before": 11,
                        "distance_after": 10,
                    }
                ],
                "stop_reason": "no_improving_move",
            }
        raise AssertionError(f"unexpected tree0: {tree0}")

    monkeypatch.setattr(probe, "encode", fake_encode)
    monkeypatch.setattr(probe, "lookahead_pathwise_build_toward_target", fake_lookahead)

    seed_family = [
        {
            "seed": 100,
            "source": "scale_anchor",
            "source_rank": 1,
            "distance_to_target": 10,
            "priority_key": (1, 10, 100, 0),
        },
        {
            "seed": 101,
            "source": "scale_anchor",
            "source_rank": 1,
            "distance_to_target": 10,
            "priority_key": (1, 10, 101, 1),
        },
    ]

    report = probe.choose_best_seed_toward_target(
        target=100,
        seed_ns=seed_family,
        builder="lookahead",
        step_limit=5,
        limit=100,
        policy="scale_first",
    )

    static = next(item for item in report["candidates"] if item["seed_n"] == 100)
    constructive = next(item for item in report["candidates"] if item["seed_n"] == 101)

    assert static["final_distance"] == constructive["final_distance"] == 10
    assert static["seed_source"] == constructive["seed_source"] == "scale_anchor"
    assert static["seed_distance_to_target"] == constructive["seed_distance_to_target"] == 10
    assert static["step_count"] == 0
    assert constructive["step_count"] > 0

    assert report["best_seed"] == 101
