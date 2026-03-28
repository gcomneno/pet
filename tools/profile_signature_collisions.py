#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


def shape_sig_from_exp(e):
    if e is None:
        return ()
    return shape_sig_from_pet(e)


def shape_sig_from_pet(pet):
    return tuple(sorted(shape_sig_from_exp(node["e"]) for node in pet))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Find branch_profile collisions by distinct PET shape signatures."
    )
    parser.add_argument("dataset", help="PET JSONL dataset path")
    parser.add_argument(
        "--progress-every",
        type=int,
        default=100000,
        help="print a progress line every N scanned records (default: 100000)",
    )
    parser.add_argument(
        "--min-collisions",
        type=int,
        default=2,
        help="show only profiles with at least this many distinct signatures (default: 2)",
    )
    args = parser.parse_args()

    dataset = Path(args.dataset)
    if not dataset.is_file():
        raise SystemExit(f"dataset not found: {dataset}")

    records = 0
    profiles = defaultdict(dict)  # profile -> {shape_sig: first_n}

    with dataset.open(encoding="utf-8") as fh:
        for line in fh:
            rec = json.loads(line)
            profile = tuple(rec["metrics"]["branch_profile"])
            sig = shape_sig_from_pet(rec["pet"])
            profiles[profile].setdefault(sig, rec["n"])
            records += 1

            if args.progress_every > 0 and records % args.progress_every == 0:
                print(f"scanned {records}")

    print()
    print("=== collisions by branch_profile ===")

    found = 0
    for profile, shapes in sorted(profiles.items(), key=lambda kv: (len(kv[0]), kv[0])):
        if len(shapes) < args.min_collisions:
            continue
        gens = sorted(shapes.values())
        print(
            f"profile={list(profile)} "
            f"distinct_signatures={len(shapes)} "
            f"generators={gens}"
        )
        found += 1

    if found == 0:
        print("no collisions found")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
