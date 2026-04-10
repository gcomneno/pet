#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import tools.partial_signature_probe as probe_mod
from tools.pet_hybrid_bridge import build_bridge
from tools.pet_hybrid_synthesize import build_candidates


def build_partial_explain(n: int, schedule: list[int]) -> dict[str, Any]:
    old_trace = probe_mod._TRACE_ENABLED
    try:
        probe_mod._TRACE_ENABLED = False
        probe = probe_mod.build_report(n, schedule)
    finally:
        probe_mod._TRACE_ENABLED = old_trace

    bridge = build_bridge(probe)
    synthesis = build_candidates(bridge)

    return {
        "n": n,
        "schedule": schedule,
        "probe": {
            "stop_reason": probe["stop_reason"],
            "closure_kind": probe["closure_kind"],
            "last_progress_stage_kind": probe["last_progress_stage_kind"],
            "stalled": probe["stalled"],
            "rho_used": probe["rho_used"],
            "known_factors": probe["known_factors"],
            "known_root_children": probe["known_root_children"],
            "known_root_generator_lower_bound": probe["known_root_generator_lower_bound"],
            "residual": probe["residual"],
            "residual_info": probe["residual_info"],
            "root_generator_lower_bound": probe["root_generator_lower_bound"],
            "exact_root_anatomy": probe["exact_root_anatomy"],
            "exact_root_children": probe["exact_root_children"],
            "exact_root_generator": probe["exact_root_generator"],
            "fully_factored": probe["fully_factored"],
        },
        "candidate_count": synthesis["candidate_count"],
        "top_candidate": synthesis["candidates"][0] if synthesis["candidates"] else None,
        "candidates": synthesis["candidates"],
    }


def render_human(data: dict[str, Any]) -> str:
    probe = data["probe"]
    lines: list[str] = []

    lines.append(f"N = {data['n']}")
    lines.append(f"schedule = {data['schedule']}")
    lines.append(f"stop_reason = {probe['stop_reason']}")
    lines.append(f"closure_kind = {probe['closure_kind']}")
    lines.append(f"exact_root_anatomy = {probe['exact_root_anatomy']}")
    lines.append(f"known_root_children = {probe['known_root_children']}")
    lines.append(
        f"known_root_generator_lower_bound = {probe['known_root_generator_lower_bound']}"
    )
    lines.append(f"root_generator_lower_bound = {probe['root_generator_lower_bound']}")
    lines.append(f"residual_status = {probe['residual_info']['status']}")
    lines.append(f"residual_digits = {len(str(probe['residual']))}")

    if probe["exact_root_children"] is not None:
        lines.append(f"exact_root_children = {probe['exact_root_children']}")
        lines.append(f"exact_root_generator = {probe['exact_root_generator']}")

    lines.append(f"candidate_count = {data['candidate_count']}")

    top = data["top_candidate"]
    if top is not None:
        lines.append("")
        lines.append("top_candidate:")
        lines.append(f"  rank = {top['rank']}")
        lines.append(f"  kind = {top['candidate_kind']}")
        lines.append(f"  root_generator = {top['candidate_root_generator']}")
        lines.append(f"  root_children = {top['candidate_root_children']}")

    if data["candidates"]:
        lines.append("")
        lines.append("top_candidates:")
        for c in data["candidates"][:3]:
            lines.append(
                f"  [{c['rank']}] kind={c['candidate_kind']} "
                f"root_generator={c['candidate_root_generator']} "
                f"root_children={c['candidate_root_children']}"
            )

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run Partial-PET probe + hybrid synthesis and show the top candidate(s)."
    )
    parser.add_argument("n", type=int, help="Integer to inspect")
    parser.add_argument(
        "--schedule",
        default="100,1000,10000",
        help="Comma-separated probe schedule, e.g. 10 or 100,1000,10000",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    if args.n < 1:
        print("ERROR: N must be >= 1", file=sys.stderr)
        return 2

    try:
        schedule = probe_mod.parse_schedule(args.schedule)
        data = build_partial_explain(args.n, schedule)

        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print(render_human(data))

        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
