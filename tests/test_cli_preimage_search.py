from __future__ import annotations

import json
import subprocess
import sys


def test_cli_preimage_search_json_open_case():
    proc = subprocess.run(
        [
            "pet",
            "preimage-search",
            "84739348317483740132",
            "--schedule",
            "10",
            "--mode",
            "quick",
            "--depth",
            "6",
            "--json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)

    assert data["schema"] == "pet-preimage-profiled-search-report-v0"
    assert data["source_n"] == 84739348317483740132
    assert data["mode"] == "quick"
    assert data["depth"] == 6
    assert data["profile"] == {
        "rank": 1,
        "max_target_n": 5_000_000,
        "max_new_in_path": 2,
        "require_known_children_covered": True,
    }
    assert data["frontier_count"] == 17
    assert data["min_n"] == 40320
    assert data["max_n"] == 3603600
    assert data["sample_ns"][:8] == [40320, 60480, 90720, 100800, 151200, 221760, 226800, 332640]


def test_cli_preimage_search_json_exact_case():
    proc = subprocess.run(
        [
            "pet",
            "preimage-search",
            "4452484",
            "--schedule",
            "10",
            "--mode",
            "quick",
            "--depth",
            "6",
            "--json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)

    assert data["schema"] == "pet-preimage-profiled-search-report-v0"
    assert data["source_n"] == 4452484
    assert data["mode"] == "quick"
    assert data["depth"] == 6
    assert data["profile"] == {
        "rank": 1,
        "max_target_n": 5_000_000,
        "max_new_in_path": 2,
        "require_known_children_covered": False,
    }
    assert data["frontier_count"] == 24
    assert data["min_n"] == 26880
    assert data["max_n"] == 3603600
    assert data["sample_ns"][:8] == [26880, 40320, 60480, 90720, 100800, 147840, 151200, 221760]
