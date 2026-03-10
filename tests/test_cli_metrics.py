#!/usr/bin/env python3

import subprocess
import sys


def test_cli_metrics():
    result = subprocess.run(
        [sys.executable, "src/pet.py", "--metrics", "256"],
        capture_output=True,
        text=True,
        check=True,
    )

    expected = [
        "N = 256",
        "node_count = 3",
        "leaf_count = 1",
        "height = 3",
    ]

    output_lines = result.stdout.strip().splitlines()
    assert output_lines == expected, f"unexpected output: {result.stdout!r}"


if __name__ == "__main__":
    test_cli_metrics()
    print("OK")
