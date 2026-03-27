import json
import subprocess
import sys


def test_cli_compare_json():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pet.cli",
            "compare",
            "12",
            "18",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    data = json.loads(result.stdout)

    assert data["n1"] == 12
    assert data["n2"] == 18
    assert data["distance"] == 2
    assert data["structural_distance"] == 0
    assert data["same_shape"] is True
