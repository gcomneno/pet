#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pet.core import is_prime, prime_factorization, shape_signature_dict


def factor_map(n: int) -> dict[int, int]:
    return {p: e for p, e in prime_factorization(n)}


def exp_signature(exp: int):
    if exp < 1:
        raise ValueError("exp must be >= 1")
    if exp == 1:
        return []
    return shape_signature_dict(exp)["signature"]


def apply_step(current: int, step: dict, index: int) -> dict:
    if current < 1:
        raise ValueError("current must be >= 1")

    if not isinstance(step, dict):
        raise TypeError(f"step #{index}: step must be an object")

    op = step.get("op")
    prime = step.get("prime")

    if op not in {"attach", "bump"}:
        raise ValueError(f"step #{index}: unsupported op {op!r}")

    if not isinstance(prime, int):
        raise TypeError(f"step #{index}: prime must be an int")

    if not is_prime(prime):
        raise ValueError(f"step #{index}: {prime} is not prime")

    before_map = {} if current == 1 else factor_map(current)
    already_present = prime in before_map

    if op == "attach" and already_present:
        raise ValueError(
            f"step #{index}: attach requires a new prime, but {prime} already divides {current}"
        )

    if op == "bump" and not already_present:
        raise ValueError(
            f"step #{index}: bump requires an existing prime, but {prime} does not divide {current}"
        )

    exp_before = before_map.get(prime, 0)
    after = current * prime
    after_map = factor_map(after)
    exp_after = after_map[prime]

    branch_before = None if exp_before == 0 else exp_signature(exp_before)
    branch_after = exp_signature(exp_after)
    before_signature = None if current == 1 else shape_signature_dict(current)["signature"]

    return {
        "index": index,
        "op": op,
        "prime": prime,
        "before": current,
        "after": after,
        "exp_before": exp_before,
        "exp_after": exp_after,
        "branch_before": branch_before,
        "branch_after": branch_after,
        "before_signature": before_signature,
        "after_signature": shape_signature_dict(after)["signature"],
    }


def expand_steps(steps: list[dict]) -> list[dict]:
    expanded = []

    for index, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            raise TypeError(f"step #{index}: step must be an object")

        repeat = step.get("repeat", 1)
        if not isinstance(repeat, int):
            raise TypeError(f"step #{index}: repeat must be an int")
        if repeat < 1:
            raise ValueError(f"step #{index}: repeat must be >= 1")

        base_step = {k: v for k, v in step.items() if k != "repeat"}
        expanded.extend(base_step for _ in range(repeat))

    return expanded


def execute_plan(plan: dict) -> dict:
    if not isinstance(plan, dict):
        raise TypeError("plan must be a JSON object")

    start = plan.get("start")
    steps = plan.get("steps")

    if not isinstance(start, int):
        raise TypeError("plan.start must be an int")
    if start < 1:
        raise ValueError("plan.start must be >= 1")

    if not isinstance(steps, list):
        raise TypeError("plan.steps must be a list")

    expanded_steps = expand_steps(steps)

    current = start
    history = []

    for index, step in enumerate(expanded_steps, start=1):
        report = apply_step(current, step, index)
        history.append(report)
        current = report["after"]

    final_info = shape_signature_dict(current)

    return {
        "start": start,
        "declared_step_count": len(steps),
        "expanded_step_count": len(expanded_steps),
        "final_n": current,
        "generator": final_info["generator"],
        "already_minimal": final_info["already_minimal"],
        "signature": final_info["signature"],
        "child_generators": final_info["child_generators"],
        "history": history,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Execute a research-facing constructive PET plan."
    )
    parser.add_argument("plan", help="Path to JSON plan file")
    parser.add_argument("--json", action="store_true", help="Emit JSON report")
    args = parser.parse_args()

    try:
        plan_path = Path(args.plan)
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        report = execute_plan(plan)

        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print(f"start = {report['start']}")
            print(f"declared_step_count = {report['declared_step_count']}")
            print(f"expanded_step_count = {report['expanded_step_count']}")
            print(f"final_n = {report['final_n']}")
            print(f"generator = {report['generator']}")
            print(f"already_minimal = {report['already_minimal']}")
            print(f"child_generators = {report['child_generators']}")
            print(f"signature = {report['signature']}")
            print("history:")
            for item in report["history"]:
                print(
                    f"  #{item['index']}: {item['op']} p={item['prime']} "
                    f"{item['before']} -> {item['after']} "
                    f"(exp {item['exp_before']} -> {item['exp_after']}) "
                    f"branch {item['branch_before']} -> {item['branch_after']}"
                )

        return 0

    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
