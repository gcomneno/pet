#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def shape_sig_from_exp(e):
    if e is None:
        return ()
    return shape_sig_from_pet(e)


def shape_sig_from_pet(pet):
    return tuple(sorted(shape_sig_from_exp(node["e"]) for node in pet))


def encode_sig(sig):
    if not sig:
        return 1
    primes = []
    candidate = 2
    while len(primes) < len(sig):
        ok = True
        for p in primes:
            if p * p > candidate:
                break
            if candidate % p == 0:
                ok = False
                break
        if ok:
            primes.append(candidate)
        candidate += 1 if candidate == 2 else 2

    child_generators = sorted((encode_sig(child) for child in sig), reverse=True)
    n = 1
    for p, e in zip(primes, child_generators):
        n *= p ** e
    return n


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Dump distinct PET signatures for a given branch_profile."
    )
    parser.add_argument("dataset", help="PET JSONL dataset path")
    parser.add_argument(
        "profile",
        help='target branch_profile, for example "[3,3,1]"',
    )
    args = parser.parse_args()

    dataset = Path(args.dataset)
    if not dataset.is_file():
        raise SystemExit(f"dataset not found: {dataset}")

    try:
        target = json.loads(args.profile)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid profile JSON: {exc}") from exc

    if not isinstance(target, list) or not all(isinstance(x, int) for x in target):
        raise SystemExit("profile must be a JSON list of integers, e.g. [3,3,1]")

    found = {}

    with dataset.open(encoding="utf-8") as fh:
        for line in fh:
            rec = json.loads(line)
            if rec["metrics"]["branch_profile"] != target:
                continue
            sig = shape_sig_from_pet(rec["pet"])
            found.setdefault(sig, rec["n"])

    items = sorted(found.items(), key=lambda kv: kv[1])

    print(f"profile = {target}")
    print(f"distinct_signatures = {len(items)}")
    print()

    for sig, n in items:
        child_generators = sorted((encode_sig(child) for child in sig), reverse=True)
        print(f"generator = {n}")
        print(f"child_generators = {child_generators}")
        print(f"signature = {sig}")
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
