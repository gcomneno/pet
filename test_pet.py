from pet import encode, decode

SAMPLES = [
    2,
    3,
    4,
    12,
    18,
    72,
    144,
    256,
    512,
    1024,
    65536,
]

for n in SAMPLES:
    tree = encode(n)
    back = decode(tree)
    assert back == n, f"roundtrip failed for {n}: got {back}"

print("OK: all PET roundtrip tests passed.")
