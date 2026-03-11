#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pet import decode, encode

SAMPLES = [
    # potenze di un solo primo
    2,
    4,
    8,
    16,
    32,
    64,
    128,
    256,
    512,
    1024,
    2048,
    4096,
    8192,
    65536,
    # due fattori distinti
    6,
    10,
    12,
    15,
    18,
    20,
    28,
    30,
    45,
    50,
    # tre o più fattori distinti
    30,
    42,
    60,
    66,
    70,
    72,
    84,
    90,
    105,
    210,
    360,
    # esponenti grandi con basi miste
    2**3 * 3**5,  # 8 * 243 = 1944
    2**5 * 7**2,  # 32 * 49 = 1568
    3**4 * 5**3,  # 81 * 125 = 10125
    2**2 * 3**3 * 5,  # 4 * 27 * 5 = 540
    2 * 3 * 5 * 7 * 11 * 13,  # primo sestuplo: 30030
]


def test_pet_roundtrip_samples():
    for n in SAMPLES:
        tree = encode(n)
        back = decode(tree)
        assert back == n, f"roundtrip failed for {n}: got {back}"
