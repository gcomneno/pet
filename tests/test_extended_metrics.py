#!/usr/bin/env python3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pet import encode
from pet_metrics import extended_metrics, verticality_ratio, structural_asymmetry, is_linear, is_level_uniform


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


@pytest.mark.parametrize("n, expected", [
    (2,    True),
    (32,   True),   # 2^5, esponente primo
    (256,  True),   # 2^(2^3), catena
    (512,  True),   # 2^(3^2), catena
    (64,   False),  # 2^(2*3), esponente composto
    (1024, False),  # 2^(2*5), esponente composto
    (6,    False),  # 2*3, due fattori distinti
    (12,   False),  # 2^2*3
])
def test_is_linear(n, expected):
    tree = encode(n)
    assert is_linear(tree) == expected, f"is_linear failed for {n}"


@pytest.mark.parametrize("n, expected", [
    (2,   True),   # [1]
    (4,   True),   # [1, 1]
    (16,  True),   # [1, 1, 1]
    (36,  True),   # [2, 2]
    (72,  True),   # [2, 2]
    (256, True),   # [1, 1, 1]
    (12,  False),  # [2, 1]
    (48,  False),  # [2, 1, 1]
    (360, False),  # [3, 2]
])
def test_is_level_uniform(n, expected):
    tree = encode(n)
    assert is_level_uniform(tree) == expected, f"is_level_uniform failed for {n}"
