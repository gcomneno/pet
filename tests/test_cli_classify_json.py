import json
import subprocess
import sys


def test_cli_classify_json():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pet.cli",
            "classify",
            "72",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    data = json.loads(result.stdout)

    assert data["n"] == 72
    assert data["is_linear"] is False
    assert data["is_level_uniform"] is True
    assert data["is_expanding"] is False
    assert data["is_squarefree"] is False
    assert data["leaf_ratio"] == "1/2"
    assert data["profile_shape"] == "normal"
