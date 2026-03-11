#!/usr/bin/env python3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pet import encode
from pet_metrics import extended_metrics, verticality_ratio, structural_asymmetry


@pytest.mark.parametrize("n, expected_vr, expected_sa", [
    (2,   1.0,              0.0),   # singolo nodo
    (256, 1.0,              0.0),   # catena lineare pura
    (72,  0.5,              0.0),   # due livelli uniformi
    (12,  2/3,              0.5),   # due livelli asimmetrici
    (360, 0.4,              0.5),   # largo e asimmetrico
])
def test_verticality_and_asymmetry(n, expected_vr, expected_sa):
    tree = encode(n)
    assert abs(verticality_ratio(tree) - expected_vr) < 1e-9, f"verticality_ratio failed for {n}"
    assert abs(structural_asymmetry(tree) - expected_sa) < 1e-9, f"structural_asymmetry failed for {n}"


def test_extended_metrics_contains_all_keys():
    tree = encode(360)
    m = extended_metrics(tree)
    expected_keys = {
        "node_count", "leaf_count", "height", "max_branching",
        "branch_profile", "recursive_mass",
        "verticality_ratio", "structural_asymmetry",
    }
    assert set(m.keys()) == expected_keys
