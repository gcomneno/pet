import json
import subprocess
import sys


def test_cli_xmetrics_json():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pet.cli",
            "xmetrics",
            "72",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    data = json.loads(result.stdout)

    assert data["node_count"] == 4
    assert data["leaf_count"] == 2
    assert data["height"] == 2
    assert data["max_branching"] == 2
    assert data["recursive_mass"] == 2

    assert "verticality_ratio" in data
    assert "structural_asymmetry" in data
    assert "subtree_mixing_score" in data
    assert "has_root_mixed_simple_pattern" in data
