#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def load_report(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError("synthesizer report must be a JSON object")
    return data


def require_field(obj: dict[str, Any], name: str) -> Any:
    if name not in obj:
        raise KeyError(f"missing required field: {name}")
    return obj[name]


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False

    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def first_primes(count: int) -> list[int]:
    primes: list[int] = []
    candidate = 2

    while len(primes) < count:
        if is_prime(candidate):
            primes.append(candidate)
        candidate += 1 if candidate == 2 else 2

    return primes


def generator_from_signature(sig: list) -> int:
    if not sig:
        return 1

    child_generators = [generator_from_signature(child) for child in sig]
    child_generators.sort(reverse=True)

    result = 1
    for prime, exp_generator in zip(first_primes(len(child_generators)), child_generators):
        result *= prime ** exp_generator
    return result


def select_candidate(report: dict[str, Any], rank: int) -> dict[str, Any]:
    candidates = require_field(report, "candidates")
    if not isinstance(candidates, list):
        raise TypeError("candidates must be a list")

    for candidate in candidates:
        if candidate.get("rank") == rank:
            return candidate

    raise ValueError(f"no candidate found with rank={rank}")


def build_plan(report: dict[str, Any], rank: int) -> dict[str, Any]:
    schema = require_field(report, "schema")
    target_n = require_field(report, "target_n")
    candidate = select_candidate(report, rank)

    candidate_root_children = require_field(candidate, "candidate_root_children")
    candidate_kind = require_field(candidate, "candidate_kind")

    if not isinstance(candidate_root_children, list):
        raise TypeError("candidate_root_children must be a list")

    root_items = [
        {
            "signature": sig,
            "exp_generator": generator_from_signature(sig),
        }
        for sig in candidate_root_children
    ]
    root_items.sort(key=lambda item: item["exp_generator"], reverse=True)

    root_primes = first_primes(len(root_items))
    root_exponents = [item["exp_generator"] for item in root_items]
    candidate_root_children = [item["signature"] for item in root_items]

    steps: list[dict[str, int | str]] = []
    current = 1

    for prime, exp in zip(root_primes, root_exponents):
        if exp < 1:
            raise ValueError("root exponent must be >= 1")

        for i in range(exp):
            op = "attach" if i == 0 else "bump"
            steps.append({"op": op, "prime": prime})
            current *= prime

    return {
        "schema": "pet-candidate-plan-v0",
        "source_synth_schema": schema,
        "source_target_n": target_n,
        "selected_rank": rank,
        "candidate_kind": candidate_kind,
        "candidate_root_children": candidate_root_children,
        "root_primes": root_primes,
        "root_exponents": root_exponents,
        "start": 1,
        "step_count": len(steps),
        "steps": steps,
        "final_n": current,
        "matches_candidate_root_generator": (
            current == candidate.get("candidate_root_generator")
        ),
        "candidate_root_generator": candidate.get("candidate_root_generator"),
    }


def render_human(plan: dict[str, Any]) -> str:
    lines = []
    lines.append(f"schema = {plan['schema']}")
    lines.append(f"source_synth_schema = {plan['source_synth_schema']}")
    lines.append(f"source_target_n = {plan['source_target_n']}")
    lines.append(f"selected_rank = {plan['selected_rank']}")
    lines.append(f"candidate_kind = {plan['candidate_kind']}")
    lines.append(f"candidate_root_children = {plan['candidate_root_children']}")
    lines.append(f"root_primes = {plan['root_primes']}")
    lines.append(f"root_exponents = {plan['root_exponents']}")
    lines.append(f"start = {plan['start']}")
    lines.append(f"step_count = {plan['step_count']}")
    lines.append(f"final_n = {plan['final_n']}")
    lines.append(
        f"candidate_root_generator = {plan['candidate_root_generator']}"
    )
    lines.append(
        f"matches_candidate_root_generator = {plan['matches_candidate_root_generator']}"
    )
    lines.append("steps:")
    for i, step in enumerate(plan["steps"], start=1):
        lines.append(f"  #{i}: {step['op']} p={step['prime']}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a minimal forward PET plan for a ranked hybrid synthesis candidate."
    )
    parser.add_argument("report", help="Path to pet_hybrid_synthesize JSON report")
    parser.add_argument(
        "--rank",
        type=int,
        default=1,
        help="Candidate rank to materialize (default: 1)",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    try:
        report = load_report(Path(args.report))
        plan = build_plan(report, args.rank)

        if args.json:
            print(json.dumps(plan, ensure_ascii=False, indent=2))
        else:
            print(render_human(plan))

        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
