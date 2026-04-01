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
        raise TypeError("probe report must be a JSON object")
    return data


def require_field(report: dict[str, Any], name: str) -> Any:
    if name not in report:
        raise KeyError(f"missing required field: {name}")
    return report[name]


def build_bridge(report: dict[str, Any]) -> dict[str, Any]:
    n = require_field(report, "n")
    schedule = require_field(report, "schedule")
    known_factors = require_field(report, "known_factors")
    known_root_children = require_field(report, "known_root_children")
    known_root_generator_lower_bound = require_field(report, "known_root_generator_lower_bound")
    residual = require_field(report, "residual")
    residual_info = require_field(report, "residual_info")
    root_generator_lower_bound = require_field(report, "root_generator_lower_bound")
    exact_root_anatomy = require_field(report, "exact_root_anatomy")
    exact_root_children = report.get("exact_root_children")
    exact_root_generator = report.get("exact_root_generator")
    fully_factored = require_field(report, "fully_factored")
    stop_reason = require_field(report, "stop_reason")
    closure_kind = report.get("closure_kind")
    last_progress_stage_kind = report.get("last_progress_stage_kind")
    rho_used = report.get("rho_used")
    stalled = report.get("stalled")

    if not isinstance(known_factors, list):
        raise TypeError("known_factors must be a list")
    if not isinstance(known_root_children, list):
        raise TypeError("known_root_children must be a list")
    if not isinstance(residual_info, dict):
        raise TypeError("residual_info must be an object")

    hard_constraints = {
        "known_factors": known_factors,
        "known_root_children": known_root_children,
        "known_root_generator_lower_bound": known_root_generator_lower_bound,
        "root_generator_lower_bound": root_generator_lower_bound,
        "exact_root_anatomy": exact_root_anatomy,
        "exact_root_children": exact_root_children,
        "exact_root_generator": exact_root_generator,
        "fully_factored": fully_factored,
    }

    soft_constraints = {
        "residual": residual,
        "residual_info": residual_info,
        "stop_reason": stop_reason,
        "closure_kind": closure_kind,
        "last_progress_stage_kind": last_progress_stage_kind,
        "rho_used": rho_used,
        "stalled": stalled,
    }

    residual_status = residual_info.get("status")
    residual_root_children_lower_bound = residual_info.get("root_children_lower_bound")
    exact_children_known = residual_info.get("exact_root_children") is not None

    synthesis_hints = {
        "target_n": n,
        "schedule": schedule,
        "include_known_factors_exactly": True,
        "residual_modeling_required": not bool(exact_root_anatomy),
        "residual_status": residual_status,
        "residual_root_children_lower_bound": residual_root_children_lower_bound,
        "prefer_minimal_completion": True,
        "allow_multiple_candidates": True,
        "treat_lower_bounds_as_exact": False,
        "treat_residual_as_recovered": False,
        "exact_children_known_at_residual_level": exact_children_known,
    }

    return {
        "schema": "pet-hybrid-bridge-v0",
        "target": {
            "n": n,
            "schedule": schedule,
        },
        "hard_constraints": hard_constraints,
        "soft_constraints": soft_constraints,
        "synthesis_hints": synthesis_hints,
    }


def render_human(bridge: dict[str, Any]) -> str:
    lines = []
    lines.append(f"schema = {bridge['schema']}")
    lines.append(f"target_n = {bridge['target']['n']}")
    lines.append(f"schedule = {bridge['target']['schedule']}")
    lines.append("")
    lines.append("hard_constraints:")
    for key, value in bridge["hard_constraints"].items():
        lines.append(f"  {key} = {value}")
    lines.append("")
    lines.append("soft_constraints:")
    for key, value in bridge["soft_constraints"].items():
        lines.append(f"  {key} = {value}")
    lines.append("")
    lines.append("synthesis_hints:")
    for key, value in bridge["synthesis_hints"].items():
        lines.append(f"  {key} = {value}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Translate partial_signature_probe JSON into a hybrid reconstruction bridge payload."
    )
    parser.add_argument("report", help="Path to partial_signature_probe JSON report")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    try:
        report = load_report(Path(args.report))
        bridge = build_bridge(report)

        if args.json:
            print(json.dumps(bridge, ensure_ascii=False, indent=2))
        else:
            print(render_human(bridge))

        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
