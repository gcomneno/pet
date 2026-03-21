#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path


def test_atlas_summary_small_scan(tmp_path):
    jsonl_path = tmp_path / "scan.jsonl"

    subprocess.run(
        [
            sys.executable,
            "-m",
            "pet.cli",
            "scan",
            "2",
            "12",
            "--jsonl",
            str(jsonl_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    result = subprocess.run(
        [sys.executable, "tools/atlas_summary.py", str(jsonl_path)],
        check=True,
        capture_output=True,
        text=True,
    )

    expected = """total_records: 11
distinct_shapes: 4
shape_entropy: 1.240684291953
max_entropy: 1.386294361120
max_node_count: 3
first_n_with_max_node_count: 12
max_height: 2
first_n_with_max_height: 4
max_branching: 2
first_n_with_max_branching: 6

[height_distribution]
1 7
2 4

[max_branching_distribution]
1 8
2 3
"""
    assert result.stdout == expected
