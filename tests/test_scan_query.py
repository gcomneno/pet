#!/usr/bin/env python3
import subprocess
import sys


def test_scan_query_filter_height_and_branching(tmp_path):
    jsonl_path = tmp_path / "scan.jsonl"

    subprocess.run(
        [
            sys.executable,
            "-m",
            "pet.cli",
            "scan",
            "2",
            "30",
            "--jsonl",
            str(jsonl_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    result = subprocess.run(
        [
            sys.executable,
            "tools/scan_query.py",
            "filter",
            str(jsonl_path),
            "--where",
            "height=2",
            "--where",
            "max_branching>=2",
            "--limit",
            "5",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    expected = """{"schema_version": 1, "n": 12, "pet": [{"p": 2, "e": [{"p": 2, "e": null}]}, {"p": 3, "e": null}], "metrics": {"node_count": 3, "leaf_count": 2, "height": 2, "max_branching": 2, "branch_profile": [2, 1], "recursive_mass": 1, "average_leaf_depth": 1.5}, "meta": {"pet_format": "canonical-json"}}
{"schema_version": 1, "n": 18, "pet": [{"p": 2, "e": null}, {"p": 3, "e": [{"p": 2, "e": null}]}], "metrics": {"node_count": 3, "leaf_count": 2, "height": 2, "max_branching": 2, "branch_profile": [2, 1], "recursive_mass": 1, "average_leaf_depth": 1.5}, "meta": {"pet_format": "canonical-json"}}
{"schema_version": 1, "n": 20, "pet": [{"p": 2, "e": [{"p": 2, "e": null}]}, {"p": 5, "e": null}], "metrics": {"node_count": 3, "leaf_count": 2, "height": 2, "max_branching": 2, "branch_profile": [2, 1], "recursive_mass": 1, "average_leaf_depth": 1.5}, "meta": {"pet_format": "canonical-json"}}
{"schema_version": 1, "n": 24, "pet": [{"p": 2, "e": [{"p": 3, "e": null}]}, {"p": 3, "e": null}], "metrics": {"node_count": 3, "leaf_count": 2, "height": 2, "max_branching": 2, "branch_profile": [2, 1], "recursive_mass": 1, "average_leaf_depth": 1.5}, "meta": {"pet_format": "canonical-json"}}
{"schema_version": 1, "n": 28, "pet": [{"p": 2, "e": [{"p": 2, "e": null}]}, {"p": 7, "e": null}], "metrics": {"node_count": 3, "leaf_count": 2, "height": 2, "max_branching": 2, "branch_profile": [2, 1], "recursive_mass": 1, "average_leaf_depth": 1.5}, "meta": {"pet_format": "canonical-json"}}
"""
    assert result.stdout == expected


def test_scan_query_group_count_branch_profile(tmp_path):
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
        [
            sys.executable,
            "tools/scan_query.py",
            "group-count",
            str(jsonl_path),
            "--field",
            "branch_profile",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    expected = """[1]\t5
[1, 1]\t3
[2]\t2
[2, 1]\t1
"""
    normalized = "\n".join(line.split() for line in [])
    assert "\n".join(" ".join(line.split()) for line in result.stdout.strip().splitlines()) == \
        "\n".join(" ".join(line.split()) for line in expected.strip().splitlines())
