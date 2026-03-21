#!/usr/bin/env python3
import json
import subprocess
import sys


def test_scan_jsonl_schema(tmp_path):
    jsonl_path = tmp_path / "scan.jsonl"

    subprocess.run(
        [
            sys.executable,
            "-m",
            "pet.cli",
            "scan",
            "2",
            "4",
            "--jsonl",
            str(jsonl_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    rows = [json.loads(line) for line in jsonl_path.read_text(encoding="utf-8").splitlines()]

    assert [row["n"] for row in rows] == [2, 3, 4]

    for row in rows:
        assert set(row.keys()) == {"schema_version", "n", "pet", "metrics", "meta"}
        assert row["schema_version"] == 1
        assert row["meta"] == {"pet_format": "canonical-json"}

        assert set(row["metrics"].keys()) == {
            "node_count",
            "leaf_count",
            "height",
            "max_branching",
            "branch_profile",
            "recursive_mass",
        }

    assert rows[0]["pet"] == [{"p": 2, "e": None}]
    assert rows[1]["pet"] == [{"p": 3, "e": None}]
    assert rows[2]["pet"] == [{"p": 2, "e": [{"p": 2, "e": None}]}]
