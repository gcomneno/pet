#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a smoke evaluation for the hybrid PET pipeline."
    )
    parser.add_argument(
        "cases",
        type=Path,
        help="Path to JSON file containing evaluation cases.",
    )
    return parser.parse_args()


def run_json_command(cmd: list[str], input_text: str | None = None) -> dict:
    proc = subprocess.run(
        cmd,
        input=input_text,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"command failed ({proc.returncode}): {' '.join(cmd)}\n{proc.stderr.strip()}"
        )
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"command did not produce valid JSON: {' '.join(cmd)}\n{exc}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        ) from exc


def write_temp_json(payload: dict) -> str:
    fh = tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False)
    try:
        json.dump(payload, fh)
        fh.flush()
        return fh.name
    finally:
        fh.close()


def probe_case(target: int, schedule: str | None) -> dict:
    cmd = [
        sys.executable,
        "tools/partial_signature_probe.py",
        "--json",
    ]
    if schedule:
        cmd.extend(["--schedule", schedule])
    cmd.append(str(target))
    return run_json_command(cmd)


def bridge_case(probe_payload: dict) -> dict:
    path = write_temp_json(probe_payload)
    try:
        return run_json_command(
            [
                sys.executable,
                "tools/pet_hybrid_bridge.py",
                path,
                "--json",
            ]
        )
    finally:
        Path(path).unlink(missing_ok=True)


def synth_case(bridge_payload: dict) -> dict:
    path = write_temp_json(bridge_payload)
    try:
        return run_json_command(
            [
                sys.executable,
                "tools/pet_hybrid_synthesize.py",
                path,
                "--json",
            ]
        )
    finally:
        Path(path).unlink(missing_ok=True)


def candidate_plan_case(synth_payload: dict, rank: int = 1) -> dict:
    path = write_temp_json(synth_payload)
    try:
        return run_json_command(
            [
                sys.executable,
                "tools/pet_candidate_plan.py",
                path,
                "--rank",
                str(rank),
                "--json",
            ]
        )
    finally:
        Path(path).unlink(missing_ok=True)


def constructive_plan_case(constructive_plan: dict) -> dict:
    path = write_temp_json(constructive_plan)
    try:
        return run_json_command(
            [
                sys.executable,
                "tools/pet_constructive_plan.py",
                path,
                "--json",
            ]
        )
    finally:
        Path(path).unlink(missing_ok=True)


def extract_top1_strategy(synth_payload: dict) -> str | None:
    candidates = synth_payload.get("candidates", []) or []
    if not candidates:
        return None
    return candidates[0].get("candidate_kind")


def extract_top1_root_generator(synth_payload: dict) -> int | None:
    candidates = synth_payload.get("candidates", []) or []
    if not candidates:
        return None
    return candidates[0].get("candidate_root_generator")


def determine_outcome(
    synth_payload: dict | None,
    plan_payload: dict | None,
    exec_payload: dict | None,
    error: str | None,
) -> str:
    if error is not None:
        return "failed"

    candidates = []
    if synth_payload is not None:
        candidates = synth_payload.get("candidates", []) or []

    if not candidates:
        return "no_candidate"

    if plan_payload is None:
        return "planner_failed"

    if plan_payload.get("matches_candidate_root_generator") is not True:
        return "mismatch"

    if exec_payload is None:
        return "executor_failed"

    return "validated"



def build_summary(results: list[dict]) -> dict:
    summary: dict[str, dict] = {}
    for row in results:
        family = row["family"]
        bucket = summary.setdefault(
            family,
            {
                "cases": 0,
                "validated": 0,
                "no_candidate": 0,
                "planner_failed": 0,
                "executor_failed": 0,
                "mismatch": 0,
                "failed": 0,
            },
        )
        bucket["cases"] += 1
        outcome = row["outcome"]
        if outcome in bucket:
            bucket[outcome] += 1
        else:
            bucket["failed"] += 1
    return summary


def main() -> int:
    args = parse_args()

    with args.cases.open("r", encoding="utf-8") as fh:
        cases = json.load(fh)

    results = []
    for case in cases:
        target = case["target"]
        schedule = case.get("probe_schedule")

        probe = None
        bridge = None
        synth = None
        plan = None
        exec_payload = None
        error = None

        try:
            probe = probe_case(target, schedule)
            bridge = bridge_case(probe)
            synth = synth_case(bridge)

            candidates = synth.get("candidates", []) or []
            if candidates:
                plan = candidate_plan_case(synth, rank=1)
                constructive_plan = plan.get("constructive_plan")
                if constructive_plan is None:
                    raise RuntimeError("candidate plan did not contain constructive_plan")
                exec_payload = constructive_plan_case(constructive_plan)
        except Exception as exc:
            error = str(exc)

        residual_info = {}
        if probe is not None:
            residual_info = probe.get("residual_info", {}) or {}

        synthesis_hints = {}
        if bridge is not None:
            synthesis_hints = bridge.get("synthesis_hints", {}) or {}

        candidate_count = 0
        if synth is not None:
            candidate_count = len(synth.get("candidates", []) or [])

        outcome = determine_outcome(synth, plan, exec_payload, error)

        results.append(
            {
                "target": target,
                "family": case["family"],
                "label": case.get("label"),
                "probe_schedule": schedule,
                "status": residual_info.get("status"),
                "probe_stop_reason": None if probe is None else probe.get("stop_reason"),
                "probe_closure_kind": None if probe is None else probe.get("closure_kind"),
                "fully_factored": None if probe is None else probe.get("fully_factored"),
                "exact_root_anatomy": None if probe is None else probe.get("exact_root_anatomy"),
                "bridge_schema": None if bridge is None else bridge.get("schema"),
                "hard_constraint_count": 0 if bridge is None else len(bridge.get("hard_constraints", [])),
                "soft_constraint_count": 0 if bridge is None else len(bridge.get("soft_constraints", [])),
                "hint_keys": sorted(synthesis_hints.keys()),
                "synth_schema": None if synth is None else synth.get("schema"),
                "candidate_count": candidate_count,
                "top1_strategy": None if synth is None else extract_top1_strategy(synth),
                "top1_root_generator": None if synth is None else extract_top1_root_generator(synth),
                "plan_schema": None if plan is None else plan.get("schema"),
                "matches_candidate_root_generator": None if plan is None else plan.get("matches_candidate_root_generator"),
                "plan_final_n": None if plan is None else plan.get("final_n"),
                "execution_ok": exec_payload is not None,
                "executor_final_n": None if exec_payload is None else exec_payload.get("final_n"),
                "already_minimal": None if exec_payload is None else exec_payload.get("already_minimal"),
                "outcome": outcome,
                "error": error,
            }
        )

    payload = {
        "schema": "pet-hybrid-eval-v0",
        "case_count": len(cases),
        "summary_by_family": build_summary(results),
        "results": results,
    }

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
