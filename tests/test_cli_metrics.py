#!/usr/bin/env python3
import subprocess
import sys


def test_cli_metrics():
    result = subprocess.run(
        [sys.executable, "-m", "pet.cli", "metrics", "256"],
        capture_output=True,
        text=True,
        check=True,
    )

    expected = [
        "N = 256",
        "node_count = 3",
        "leaf_count = 1",
        "height = 3",
        "max_branching = 1",
        "branch_profile = [1, 1, 1]",
        "recursive_mass = 2",
        "average_leaf_depth = 3.0",
    ]

    assert result.stdout.strip().splitlines() == expected
