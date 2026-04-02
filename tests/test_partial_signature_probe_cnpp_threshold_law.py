from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from sympy import factorint

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
    # lightweight semiprime residual
    {"target": 30030, "penultimate_schedule": 10, "threshold": 11},
    # another semiprime residual with larger threshold
    {"target": 293930, "penultimate_schedule": 16, "threshold": 17},
    # multiplicity-heavy penultimate residual: 11^4 * 13
    {"target": 39969930, "penultimate_schedule": 10, "threshold": 11},
    # larger but still practical
    {"target": 6469693230, "penultimate_schedule": 22, "threshold": 23},
    # higher threshold example
    {"target": 3928638, "penultimate_schedule": 88, "threshold": 89},
]


def test_cnpp_probe_closes_when_schedule_hits_smallest_penultimate_residual_prime() -> None:
    for case in CASES:
        target = case["target"]
        penultimate_schedule = case["penultimate_schedule"]
        threshold = case["threshold"]

        before = run_probe(target, penultimate_schedule)
        after = run_probe(target, threshold)

        assert before["residual_info"]["status"] == "composite-non-prime-power"
        residual_factors = factorint(before["residual"])
        assert min(residual_factors) == threshold

        assert after["residual_info"]["status"] == "unit"
        assert after["residual"] == 1

        before_primes = [item["prime"] for item in before["known_factors"]]
        after_primes = [item["prime"] for item in after["known_factors"]]
        assert set(before_primes).issubset(set(after_primes))
        assert threshold in after_primes
