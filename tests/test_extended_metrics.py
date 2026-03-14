#!/usr/bin/env python3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pet import encode
from pet.metrics import extended_metrics, verticality_ratio, structural_asymmetry, is_linear, is_level_uniform, is_expanding, is_squarefree, leaf_ratio, profile_shape
from fractions import Fraction


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


@pytest.mark.parametrize("n, expected", [
    (64,   True),   # 2^6, esponente 6=2*3
    (576,  True),   # 2^6 * 3^2
    (729,  True),   # 3^6, esponente 6=2*3
    (1024, True),   # 2^10, esponente 10=2*5
    (2,    False),  # primo
    (12,   False),  # 2^2 * 3
    (72,   False),  # 2^3 * 3^2
    (256,  False),  # 2^8 = 2^(2^3), catena
    (360,  False),  # 2^3 * 3^2 * 5
])
def test_is_expanding(n, expected):
    tree = encode(n)
    assert is_expanding(tree) == expected, f"is_expanding failed for {n}"


@pytest.mark.parametrize("n, expected", [
    (2,   True),   # primo
    (6,   True),   # 2*3
    (30,  True),   # 2*3*5
    (42,  True),   # 2*3*7
    (4,   False),  # 2^2
    (12,  False),  # 2^2 * 3
    (72,  False),  # 2^3 * 3^2
    (360, False),  # 2^3 * 3^2 * 5
])
def test_is_squarefree(n, expected):
    tree = encode(n)
    assert is_squarefree(tree) == expected, f"is_squarefree failed for {n}"


@pytest.mark.parametrize("n, expected", [
    (2,     Fraction(1, 1)),   # primo, ratio=1
    (4,     Fraction(1, 2)),   # [1,1]
    (16,    Fraction(1, 3)),   # [1,1,1]
    (65536, Fraction(1, 4)),   # [1,1,1,1]
    (12,    Fraction(2, 3)),   # [2,1]
    (60,    Fraction(3, 4)),   # [3,1]
    (30,    Fraction(1, 1)),   # squarefree, ratio=1
    (36,    Fraction(1, 2)),   # [2,2]
    (144,   Fraction(2, 5)),   # [2,2,1]
])
def test_leaf_ratio(n, expected):
    tree = encode(n)
    assert leaf_ratio(tree) == expected, f"leaf_ratio failed for {n}"


@pytest.mark.parametrize("n, expected", [
    (2,    'point'),     # singolo nodo
    (30,   'point'),     # squarefree a 3 fattori, height=1
    (16,   'linear'),    # [1,1,1]
    (256,  'linear'),    # [1,1,1]
    (12,   'normal'),    # [2,1]
    (360,  'normal'),    # [3,2]
    (900,  'normal'),    # [3,3]
    (64,   'expanding'), # [1,2]
    (576,  'expanding'), # [2,3]
    (4096, 'bell'),      # [1,2,1]
    (5184, 'bell'),      # [2,3,1]
])
def test_profile_shape(n, expected):
    tree = encode(n)
    assert profile_shape(tree) == expected, f"profile_shape failed for {n}"
