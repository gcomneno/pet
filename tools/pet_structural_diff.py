#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pet.core import prime_factorization, shape_signature_dict


def factor_map(n: int) -> dict[int, int]:
    return {p: e for p, e in prime_factorization(n)}


def exp_signature(exp: int):
    if exp < 1:
        raise ValueError("exp must be >= 1")
    if exp == 1:
        return []
    return shape_signature_dict(exp)["signature"]


def build_structural_diff(before: int, factor: int) -> dict:
    if before < 2:
        raise ValueError("before must be >= 2")
    if factor < 2:
        raise ValueError("factor must be >= 2")

    after = before * factor

    before_map = factor_map(before)
    factor_map_ = factor_map(factor)
    after_map = factor_map(after)

    attached_branches = []
    bumped_branches = []
    unchanged_branches = []

    for prime in sorted(after_map):
        exp_before = before_map.get(prime, 0)
        exp_delta = factor_map_.get(prime, 0)
        exp_after = after_map[prime]

        branch_before = None if exp_before == 0 else exp_signature(exp_before)
        branch_after = exp_signature(exp_after)

        item = {
            "prime": prime,
            "exp_before": exp_before,
            "exp_after": exp_after,
            "delta": exp_delta,
            "branch_before": branch_before,
            "branch_after": branch_after,
        }

        if exp_before == 0:
            attached_branches.append(item)
        elif exp_after > exp_before:
            bumped_branches.append(item)
        else:
            unchanged_branches.append(item)

    return {
        "before": before,
        "before_signature": shape_signature_dict(before)["signature"],
        "factor": factor,
        "factor_signature": shape_signature_dict(factor)["signature"],
        "after": after,
        "result_signature": shape_signature_dict(after)["signature"],
        "attached_count": len(attached_branches),
        "bumped_count": len(bumped_branches),
        "unchanged_count": len(unchanged_branches),
        "attached_branches": attached_branches,
        "bumped_branches": bumped_branches,
        "unchanged_branches": unchanged_branches,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Research-facing PET structural diff for multiplicative updates."
    )
    parser.add_argument("before", type=int, help="Starting integer >= 2")
    parser.add_argument("factor", type=int, help="Multiplicative factor >= 2")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    report = build_structural_diff(args.before, args.factor)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"before = {report['before']}")
        print(f"factor = {report['factor']}")
        print(f"after = {report['after']}")
        print(f"attached_branches = {report['attached_branches']}")
        print(f"bumped_branches = {report['bumped_branches']}")
        print(f"unchanged_branches = {report['unchanged_branches']}")
        print(f"result_signature = {report['result_signature']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
