from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROBE = ROOT / "tools" / "partial_signature_probe.py"
BRIDGE = ROOT / "tools" / "pet_hybrid_bridge.py"
SYNTH = ROOT / "tools" / "pet_hybrid_synthesize.py"


def run_probe(n: int, schedule: int | str) -> dict:
    proc = subprocess.run(
        [sys.executable, str(PROBE), "--json", "--schedule", str(schedule), str(n)],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(proc.stdout)


def _run_json_file_command(tool: Path, payload: dict) -> dict:
    fh = tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False)
    try:
        json.dump(payload, fh)
        fh.flush()
        path = fh.name
    finally:
        fh.close()

    try:
        proc = subprocess.run(
            [sys.executable, str(tool), path, "--json"],
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(proc.stdout)
    finally:
        Path(path).unlink(missing_ok=True)


def run_bridge(probe_payload: dict) -> dict:
    return _run_json_file_command(BRIDGE, probe_payload)


def run_synth(bridge_payload: dict) -> dict:
    return _run_json_file_command(SYNTH, bridge_payload)


def run_top1(target: int, schedule: int | str) -> dict:
    probe = run_probe(target, schedule)
    bridge = run_bridge(probe)
    synth = run_synth(bridge)
    top1 = synth["candidates"][0]
    return {
        "status": probe["residual_info"]["status"],
        "top1_kind": top1["candidate_kind"],
        "top1_root_generator": top1["candidate_root_generator"],
    }


CASES = [
    {
        "target": 3928638,
        "stable_schedules": [10, 13, 17, 19, 23],
        "stable_root_generator": 2310,
        "closure_schedule": 89,
        "closure_root_generator": 2310,
    },
    {
        "target": 20086291530,
        "stable_schedules": [10, 13, 17, 19, 23, 89],
        "stable_root_generator": 4620,
        "closure_schedule": 191,
        "closure_root_generator": 4620,
    },
]


def test_persistent_cnpp_cases_show_stable_top1_before_exact_closure() -> None:
    for case in CASES:
        target = case["target"]
        stable_root = case["stable_root_generator"]

        for schedule in case["stable_schedules"]:
            row = run_top1(target, schedule)
            assert row["status"] == "composite-non-prime-power"
            assert row["top1_kind"] == "minimal-leaf-completion"
            assert row["top1_root_generator"] == stable_root

        closed = run_top1(target, case["closure_schedule"])
        assert closed["status"] == "unit"
        assert closed["top1_kind"] == "exact-root-anatomy"
        assert closed["top1_root_generator"] == case["closure_root_generator"]


REGIME_CASES = [
    {"target": 3094, "label": "quick-closure"},
    {"target": 14586, "label": "quick-closure"},
    {"target": 30030, "label": "quick-closure"},
    {"target": 72930, "label": "quick-closure"},
    {"target": 510510, "label": "quick-closure"},
    {"target": 293930, "label": "mobile-before-closure"},
    {"target": 9699690, "label": "mobile-before-closure"},
    {"target": 223092870, "label": "mobile-before-closure"},
    {"target": 6469693230, "label": "mobile-before-closure"},
    {"target": 3928638, "label": "persistent-stable-before-closure"},
    {"target": 20086291530, "label": "persistent-stable-before-closure"},
]


HARD_CNPP_CASES = [
    {
        "target": 100000000000000000000000000000000000000000000000000000000001,
        "stable_schedules": ["100", "100,1000", "100,1000,10000", "100,1000,10000,100000"],
        "stable_root_generator": {"100": 30, "100,1000": 210, "100,1000,10000": 210, "100,1000,10000,100000": 210},
    },
    {
        "target": 100000000000000000000000000000000000000000000000000000000039,
        "stable_schedules": ["100", "100,1000", "100,1000,10000", "100,1000,10000,100000"],
        "stable_root_generator": {"100": 30, "100,1000": 30, "100,1000,10000": 30, "100,1000,10000,100000": 30},
    },
]


def classify_from_schedule_10_13(target: int) -> str:
    row10 = run_top1(target, 10)
    row13 = run_top1(target, 13)

    if row13["status"] == "unit":
        return "quick-closure"

    assert row13["status"] == "composite-non-prime-power"
    if row10["top1_root_generator"] == row13["top1_root_generator"]:
        return "persistent-stable-before-closure"
    return "mobile-before-closure"


def test_cnpp_regime_discriminant_from_schedule_10_to_13_on_current_ladder() -> None:
    for case in REGIME_CASES:
        assert classify_from_schedule_10_13(case["target"]) == case["label"]


def test_hard_cnpp_monsters_keep_minimal_top1_on_current_ladder() -> None:
    for case in HARD_CNPP_CASES:
        for schedule in case["stable_schedules"]:
            row = run_top1(case["target"], schedule)
            assert row["status"] == "composite-non-prime-power"
            assert row["top1_kind"] == "minimal-leaf-completion"
            assert row["top1_root_generator"] == case["stable_root_generator"][schedule]
