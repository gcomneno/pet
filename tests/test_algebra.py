#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pet import encode, decode, prime_factorization
from pet_algebra import graft


def is_squarefree(n: int) -> bool:
    return all(e == 1 for _, e in prime_factorization(n))


def test_graft_basic():
    """graft(PET(6), PET(2)) = PET(36)"""
    result = graft(encode(6), encode(2))
    assert decode(result) == 36


def test_graft_squarefree_squared():
    """graft(PET(n), PET(2)) = n^2 for squarefree n"""
    for n in range(2, 50):
        if is_squarefree(n):
            result = graft(encode(n), encode(2))
            assert decode(result) == n ** 2, f"failed for n={n}"


def test_graft_squarefree_cubed():
    """graft(PET(n), PET(3)) = n^3 for squarefree n"""
    for n in range(2, 30):
        if is_squarefree(n):
            result = graft(encode(n), encode(3))
            assert decode(result) == n ** 3, f"failed for n={n}"


def test_graft_deep():
    """graft(PET(2), PET(6)) = PET(64) = 2^6"""
    result = graft(encode(2), encode(6))
    assert decode(result) == 64


def test_graft_result_is_valid_pet():
    """graft always produces a valid canonical PET"""
    from pet import validate
    for a in [2, 6, 12, 30]:
        for b in [2, 3, 6]:
            result = graft(encode(a), encode(b))
            validate(result)
