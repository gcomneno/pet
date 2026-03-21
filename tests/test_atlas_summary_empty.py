#!/usr/bin/env python3
import subprocess
import sys


def test_atlas_summary_empty_input(tmp_path):
    jsonl_path = tmp_path / "empty.jsonl"
    jsonl_path.write_text("", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "tools/atlas_summary.py", str(jsonl_path)],
        check=True,
        capture_output=True,
        text=True,
    )

    expected = """total_records: 0
distinct_shapes: 0
shape_entropy: 0.000000000000
max_entropy: 0.000000000000
max_node_count: -1
first_n_with_max_node_count: None
max_height: -1
first_n_with_max_height: None
max_branching: -1
first_n_with_max_branching: None

[height_distribution]

[max_branching_distribution]
"""
    assert result.stdout == expected
