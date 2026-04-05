from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROBE = ROOT / "tools" / "partial_signature_probe.py"


def run_probe(n: int, schedule: int) -> dict:
    proc = subprocess.run(
        [sys.executable, str(PROBE), "--json", "--schedule", str(schedule), str(n)],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(proc.stdout)


CASES = [
    {"target": 30030, "penultimate_schedule": 10, "threshold": 11},
    {"target": 293930, "penultimate_schedule": 16, "threshold": 17},
    {"target": 39969930, "penultimate_schedule": 10, "threshold": 11},
    {"target": 6469693230, "penultimate_schedule": 22, "threshold": 23},
    {"target": 3928638, "penultimate_schedule": 88, "threshold": 89},
]


def test_small_residual_exact_probe_closes_already_at_penultimate_schedule() -> None:
    for case in CASES:
        target = case["target"]
        penultimate_schedule = case["penultimate_schedule"]
        threshold = case["threshold"]

        before = run_probe(target, penultimate_schedule)
        after = run_probe(target, threshold)

        assert before["residual_info"]["status"] == "unit"
        assert before["residual"] == 1
        assert before["stop_reason"] == "closed-unit"
        assert before["exact_root_anatomy"] is True
        assert before["fully_factored"] is True

        assert after["residual_info"]["status"] == "unit"
        assert after["residual"] == 1
        assert after["stop_reason"] == "closed-unit"
        assert after["exact_root_anatomy"] is True
        assert after["fully_factored"] is True

        assert before["exact_root_generator"] == after["exact_root_generator"]
        assert before["known_factors"] == after["known_factors"]
