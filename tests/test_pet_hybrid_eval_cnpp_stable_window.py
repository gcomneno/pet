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


def run_probe(n: int, schedule: int) -> dict:
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


def run_top1(target: int, schedule: int) -> dict:
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
        "stable_root_generator": 420,
        "closure_schedule": 89,
        "closure_root_generator": 2310,
    },
    {
        "target": 20086291530,
        "stable_schedules": [10, 13, 17, 19, 23, 89],
        "stable_root_generator": 1260,
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
            assert row["top1_kind"] == "grouped-leaf-completion"
            assert row["top1_root_generator"] == stable_root

        closed = run_top1(target, case["closure_schedule"])
        assert closed["status"] == "unit"
        assert closed["top1_kind"] == "exact-root-anatomy"
        assert closed["top1_root_generator"] == case["closure_root_generator"]
        assert closed["top1_root_generator"] != stable_root
