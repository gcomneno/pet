#!/usr/bin/env python3
from pet import encode, decode

SAMPLES = [
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
]

for n in SAMPLES:
    tree = encode(n)
    back = decode(tree)
    assert back == n, f"roundtrip failed for {n}: got {back}"

print("OK: all PET roundtrip tests passed.")
