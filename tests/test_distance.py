import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pet import encode
from pet.algebra import distance, structural_distance


def test_distance_identical():
    for n in [2, 6, 12, 30]:
        assert distance(encode(n), encode(n)) == 0


def test_structural_distance_identical():
    for n in [2, 6, 12, 30]:
        assert structural_distance(encode(n), encode(n)) == 0


def test_distance_same_structure_different_primes():
    """PET(2) and PET(3) differ only in prime — distance 2, sdist 0"""
    assert distance(encode(2), encode(3)) == 2
    assert structural_distance(encode(2), encode(3)) == 0


def test_distance_isomorphic_pets():
    """PET(4) and PET(9) are isomorphic — sdist 0"""
    assert structural_distance(encode(4), encode(9)) == 0
    assert distance(encode(4), encode(9)) == 4


def test_distance_mirrored_structure():
    """PET(12) and PET(18) have same shape — sdist 0"""
    assert structural_distance(encode(12), encode(18)) == 0
    assert distance(encode(12), encode(18)) == 2


def test_distance_extra_node():
    """PET(2) vs PET(30): two extra nodes"""
    assert distance(encode(2), encode(30)) == 2


def test_distance_symmetry():
    """distance is symmetric"""
    cases = [(2,3),(6,10),(4,9),(2,30),(12,18)]
    for a, b in cases:
        assert distance(encode(a), encode(b)) == distance(encode(b), encode(a))
        assert structural_distance(encode(a), encode(b)) == structural_distance(encode(b), encode(a))
