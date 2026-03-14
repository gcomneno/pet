#!/usr/bin/env python3
import json
import subprocess
import sys


def test_cli_encode_json():
    result = subprocess.run(
        [sys.executable, "-m", "pet.cli", "encode", "--json", "72"],
        capture_output=True,
        text=True,
        check=True,
    )

    data = json.loads(result.stdout)

    expected = [
        {"p": 2, "e": [{"p": 3, "e": None}]},
        {"p": 3, "e": [{"p": 2, "e": None}]},
    ]

    assert data == expected
