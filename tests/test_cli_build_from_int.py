import json
import subprocess
import sys

import pytest


def _run_cli(*args: str) -> str:
    return subprocess.check_output(
        [sys.executable, "-m", "pet.cli", *args],
        text=True,
    )


def test_cli_build_from_int_smoke():
    out = _run_cli("build-from-int", "360")

    assert "input_n = 360" in out
    assert "factors = 2^3 * 3^2 * 5" in out
    assert "target_n = 360" in out
    assert "steps = 5" in out
    assert "2 --INC(p=2,e=1)--> 4" in out
    assert "72 --NEW(p=5)--> 360" in out


def test_cli_build_from_int_json_smoke():
    out = _run_cli("build-from-int", "240", "--json")
    payload = json.loads(out)

    assert payload["input_n"] == 240
    assert payload["factors"] == [[2, 4], [3, 1], [5, 1]]
    assert payload["target_n"] == 240
    assert payload["steps"] == 5
    assert payload["path"][0]["source_n"] == 2
    assert payload["path"][-1]["target_n"] == 240


def test_cli_build_from_int_rejects_noncanonical_support():
    proc = subprocess.run(
        [sys.executable, "-m", "pet.cli", "build-from-int", "28"],
        text=True,
        capture_output=True,
    )
    assert proc.returncode != 0
    assert "NEW-canonical" in proc.stderr
