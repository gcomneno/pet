#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROBE = ROOT / "tools" / "partial_signature_probe.py"


def _trace(msg: str) -> None:
    print(f"[trace] {msg}", file=sys.stderr, flush=True)


def run_probe(n: int, schedule: str) -> dict[str, Any] | None:
    cmd = [
        sys.executable,
        str(PROBE),
        str(n),
        "--schedule",
        schedule,
        "--json",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None


def generate_candidates(
    max_small: int,
    p_start: int,
    p_stop: int,
    include_composite_square_base: bool,
) -> list[tuple[str, int]]:
    small_parts = [2, 3, 5, 6, 10, 15, 30, 42, 210]
    out: list[tuple[str, int]] = []

    for small in small_parts:
        if small > max_small:
            continue

        for p in range(p_start, p_stop + 1):
            # family 1: small * p^2
            out.append((f"{small}*{p}^2", small * p * p))

            # family 2: small * p^3
            out.append((f"{small}*{p}^3", small * p * p * p))

            # family 3: small * (2p)^2
            out.append((f"{small}*(2*{p})^2", small * (2 * p) * (2 * p)))

        if include_composite_square_base:
            for p in range(p_start, p_stop + 1):
                for q in range(p + 1, p_stop + 1):
                    # family 4: small * (p*q)^2
                    base = p * q
                    out.append((f"{small}*({p}*{q})^2", small * base * base))

    return out


def build_result(label: str, n: int, report: dict[str, Any]) -> dict[str, Any]:
    residual_info = report.get("residual_info", {})
    return {
        "label": label,
        "n": n,
        "status": residual_info.get("status"),
        "fully_factored": report.get("fully_factored"),
        "exact_root_anatomy": report.get("exact_root_anatomy"),
        "stop_reason": report.get("stop_reason"),
        "residual": report.get("residual"),
        "known_factors": report.get("known_factors"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Search simple target families for examples yielding a desired partial_signature_probe residual status."
    )
    parser.add_argument(
        "status",
        help="Desired residual_info.status, e.g. prime-power-by-sympy",
    )
    parser.add_argument(
        "--schedule",
        default="10",
        help="Probe schedule passed to partial_signature_probe.py",
    )
    parser.add_argument(
        "--max-small",
        type=int,
        default=210,
        help="Maximum small multiplier to consider",
    )
    parser.add_argument(
        "--p-start",
        type=int,
        default=101,
        help="Start of p scan range",
    )
    parser.add_argument(
        "--p-stop",
        type=int,
        default=400,
        help="End of p scan range",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of matches to print",
    )
    parser.add_argument(
        "--progress-every",
        type=int,
        default=25,
        help="Emit progress trace every N attempted candidates (0 disables progress)",
    )
    parser.add_argument(
        "--include-composite-square-base",
        action="store_true",
        help="Also search family small*(p*q)^2 with p<q",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    matches: list[dict[str, Any]] = []
    tried = 0
    candidates = generate_candidates(
        args.max_small,
        args.p_start,
        args.p_stop,
        args.include_composite_square_base,
    )

    _trace(
        f"start desired_status={args.status} schedule={args.schedule} "
        f"candidate_count={len(candidates)} "
        f"composite_square_base={args.include_composite_square_base}"
    )

    for label, n in candidates:
        tried += 1

        if args.progress_every > 0 and tried % args.progress_every == 0:
            _trace(f"progress tried={tried} matches={len(matches)} last_label={label}")

        report = run_probe(n, args.schedule)
        if report is None:
            continue

        residual_info = report.get("residual_info", {})
        status = residual_info.get("status")

        if status == args.status:
            item = build_result(label, n, report)
            matches.append(item)
            _trace(
                f"match index={len(matches)} tried={tried} "
                f"label={item['label']} n={item['n']}"
            )
            if len(matches) >= args.limit:
                break

    payload = {
        "desired_status": args.status,
        "schedule": args.schedule,
        "tried": tried,
        "match_count": len(matches),
        "matches": matches,
    }

    _trace(f"done tried={tried} match_count={len(matches)}")

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"desired_status = {payload['desired_status']}")
        print(f"schedule = {payload['schedule']}")
        print(f"tried = {payload['tried']}")
        print(f"match_count = {payload['match_count']}")
        for i, item in enumerate(matches, start=1):
            print(f"[match {i}] label = {item['label']}")
            print(f"n = {item['n']}")
            print(f"status = {item['status']}")
            print(f"fully_factored = {item['fully_factored']}")
            print(f"exact_root_anatomy = {item['exact_root_anatomy']}")
            print(f"stop_reason = {item['stop_reason']}")
            print(f"residual = {item['residual']}")
            print(f"known_factors = {item['known_factors']}")
            print("")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
