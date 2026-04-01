#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def _freeze(x: Any):
    if isinstance(x, list):
        return tuple(_freeze(y) for y in x)
    return x


def _canonicalize_signatures(sigs: list[list]) -> list[list]:
    return sorted(sigs, key=_freeze)


def _first_primes(count: int) -> list[int]:
    primes: list[int] = []
    candidate = 2

    while len(primes) < count:
        is_prime = True
        if candidate < 2:
            is_prime = False
        elif candidate == 2:
            is_prime = True
        elif candidate % 2 == 0:
            is_prime = False
        else:
            d = 3
            while d * d <= candidate:
                if candidate % d == 0:
                    is_prime = False
                    break
                d += 2

        if is_prime:
            primes.append(candidate)

        candidate += 1 if candidate == 2 else 2

    return primes


def _generator_from_signature(sig: list) -> int:
    if not sig:
        return 1

    child_generators = [_generator_from_signature(child) for child in sig]
    child_generators.sort(reverse=True)

    result = 1
    for prime, exp_generator in zip(_first_primes(len(child_generators)), child_generators):
        result *= prime ** exp_generator
    return result


def _root_generator_from_children(children: list[list]) -> int:
    if not children:
        return 1

    child_generators = [_generator_from_signature(child) for child in children]
    child_generators.sort(reverse=True)

    result = 1
    for prime, exp_generator in zip(_first_primes(len(child_generators)), child_generators):
        result *= prime ** exp_generator
    return result


def _shape_depth(sig: list) -> int:
    if not sig:
        return 1
    return 1 + max(_shape_depth(child) for child in sig)


def _score_candidate(
    candidate_root_generator: int,
    modeled_branch_count: int,
    modeled_shapes: list[list],
) -> tuple[int, dict[str, int]]:
    modeled_depth_penalty = sum(_shape_depth(sig) for sig in modeled_shapes)
    score = (
        candidate_root_generator
        + modeled_branch_count * 1000
        + modeled_depth_penalty * 10000
    )
    return score, {
        "generator_term": candidate_root_generator,
        "modeled_branch_term": modeled_branch_count * 1000,
        "modeled_depth_term": modeled_depth_penalty * 10000,
    }


def load_bridge(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError("bridge payload must be a JSON object")
    return data


def require_field(obj: dict[str, Any], name: str) -> Any:
    if name not in obj:
        raise KeyError(f"missing required field: {name}")
    return obj[name]


def _candidate_record(
    *,
    candidate_kind: str,
    exact_root_anatomy_used: bool,
    fully_factored_target: bool,
    residual_modeling_required: bool,
    known_branch_count: int,
    modeled_branch_count: int,
    candidate_root_children: list[list],
    modeled_shapes: list[list],
    known_root_generator_lower_bound: int,
    notes: list[str],
) -> dict[str, Any]:
    candidate_root_children = _canonicalize_signatures(candidate_root_children)
    candidate_root_generator = _root_generator_from_children(candidate_root_children)
    score, score_terms = _score_candidate(
        candidate_root_generator=candidate_root_generator,
        modeled_branch_count=modeled_branch_count,
        modeled_shapes=modeled_shapes,
    )

    return {
        "candidate_kind": candidate_kind,
        "exact_root_anatomy_used": bool(exact_root_anatomy_used),
        "fully_factored_target": bool(fully_factored_target),
        "residual_modeling_required": bool(residual_modeling_required),
        "known_branch_count": known_branch_count,
        "modeled_branch_count": modeled_branch_count,
        "modeled_shapes": modeled_shapes,
        "candidate_root_children": candidate_root_children,
        "candidate_root_generator": candidate_root_generator,
        "known_root_generator_lower_bound": known_root_generator_lower_bound,
        "generator_matches_known_lower_bound": (
            candidate_root_generator == known_root_generator_lower_bound
        ),
        "generator_meets_known_lower_bound": (
            candidate_root_generator >= known_root_generator_lower_bound
        ),
        "score": score,
        "score_terms": score_terms,
        "notes": notes,
    }


def build_candidates(bridge: dict[str, Any]) -> dict[str, Any]:
    schema = require_field(bridge, "schema")
    target = require_field(bridge, "target")
    hard_constraints = require_field(bridge, "hard_constraints")
    synthesis_hints = require_field(bridge, "synthesis_hints")

    target_n = require_field(target, "n")
    known_root_children = require_field(hard_constraints, "known_root_children")
    known_root_generator_lower_bound = require_field(
        hard_constraints, "known_root_generator_lower_bound"
    )
    exact_root_anatomy = require_field(hard_constraints, "exact_root_anatomy")
    exact_root_children = hard_constraints.get("exact_root_children")
    exact_root_generator = hard_constraints.get("exact_root_generator")
    fully_factored = require_field(hard_constraints, "fully_factored")

    residual_modeling_required = require_field(
        synthesis_hints, "residual_modeling_required"
    )
    residual_root_children_lower_bound = require_field(
        synthesis_hints, "residual_root_children_lower_bound"
    )

    if not isinstance(known_root_children, list):
        raise TypeError("known_root_children must be a list")
    if not isinstance(known_root_generator_lower_bound, int):
        raise TypeError("known_root_generator_lower_bound must be an int")

    candidates: list[dict[str, Any]] = []

    if exact_root_anatomy:
        if not isinstance(exact_root_children, list):
            raise TypeError("exact_root_children must be a list when exact_root_anatomy is true")

        exact_children = _canonicalize_signatures(exact_root_children)
        candidate = _candidate_record(
            candidate_kind="exact-root-anatomy",
            exact_root_anatomy_used=True,
            fully_factored_target=bool(fully_factored),
            residual_modeling_required=bool(residual_modeling_required),
            known_branch_count=len(exact_children),
            modeled_branch_count=0,
            candidate_root_children=exact_children,
            modeled_shapes=[],
            known_root_generator_lower_bound=known_root_generator_lower_bound,
            notes=[
                "candidate comes directly from exact root anatomy in the bridge payload",
                "no modeled residual completion was needed",
            ],
        )
        if exact_root_generator is not None:
            candidate["exact_root_generator_from_bridge"] = exact_root_generator
            candidate["generator_matches_exact_root_generator"] = (
                candidate["candidate_root_generator"] == exact_root_generator
            )
        candidates.append(candidate)
    else:
        if not isinstance(residual_root_children_lower_bound, int):
            raise TypeError("residual_root_children_lower_bound must be an int")
        if residual_root_children_lower_bound < 0:
            raise ValueError("residual_root_children_lower_bound must be >= 0")

        known_count = len(known_root_children)
        k = residual_root_children_lower_bound

        modeled_shapes = [[]] * k
        candidates.append(
            _candidate_record(
                candidate_kind="minimal-leaf-completion",
                exact_root_anatomy_used=False,
                fully_factored_target=bool(fully_factored),
                residual_modeling_required=bool(residual_modeling_required),
                known_branch_count=known_count,
                modeled_branch_count=k,
                candidate_root_children=list(known_root_children) + modeled_shapes,
                modeled_shapes=modeled_shapes,
                known_root_generator_lower_bound=known_root_generator_lower_bound,
                notes=[
                    "known branches come from probe-certified information",
                    "modeled branches are leaf completions matching the residual lower bound",
                ],
            )
        )

        if k >= 2:
            modeled_shapes = [[[]]] + ([[]] * (k - 2))
            grouped_children = list(known_root_children) + modeled_shapes
            candidates.append(
                _candidate_record(
                    candidate_kind="grouped-leaf-completion",
                    exact_root_anatomy_used=False,
                    fully_factored_target=bool(fully_factored),
                    residual_modeling_required=bool(residual_modeling_required),
                    known_branch_count=known_count,
                    modeled_branch_count=len(modeled_shapes),
                    candidate_root_children=grouped_children,
                    modeled_shapes=modeled_shapes,
                    known_root_generator_lower_bound=known_root_generator_lower_bound,
                    notes=[
                        "two modeled leaf contributions are grouped into one shallow structured branch",
                        "this is a synthetic completion strategy, not recovered residual anatomy",
                    ],
                )
            )

        if k >= 1:
            modeled_shapes = [[[[]]]] + ([[]] * (k - 1))
            pp_children = list(known_root_children) + modeled_shapes
            candidates.append(
                _candidate_record(
                    candidate_kind="prime-power-style-completion",
                    exact_root_anatomy_used=False,
                    fully_factored_target=bool(fully_factored),
                    residual_modeling_required=bool(residual_modeling_required),
                    known_branch_count=known_count,
                    modeled_branch_count=len(modeled_shapes),
                    candidate_root_children=pp_children,
                    modeled_shapes=modeled_shapes,
                    known_root_generator_lower_bound=known_root_generator_lower_bound,
                    notes=[
                        "residual completion prefers one deeper modeled branch over purely flat branching",
                        "this is a synthetic prime-power-style hypothesis, not recovered factorization",
                    ],
                )
            )

    candidates.sort(key=lambda c: (c["score"], c["candidate_root_generator"], c["candidate_kind"]))

    for rank, candidate in enumerate(candidates, start=1):
        candidate["rank"] = rank

    return {
        "schema": "pet-hybrid-synthesis-v2",
        "bridge_schema": schema,
        "target_n": target_n,
        "candidate_count": len(candidates),
        "candidates": candidates,
    }


def render_human(report: dict[str, Any]) -> str:
    lines = []
    lines.append(f"schema = {report['schema']}")
    lines.append(f"bridge_schema = {report['bridge_schema']}")
    lines.append(f"target_n = {report['target_n']}")
    lines.append(f"candidate_count = {report['candidate_count']}")
    lines.append("")

    for i, candidate in enumerate(report["candidates"], start=1):
        lines.append(f"[candidate {i}] rank = {candidate['rank']} kind = {candidate['candidate_kind']}")
        lines.append(f"score = {candidate['score']}")
        lines.append(f"score_terms = {candidate['score_terms']}")
        lines.append(f"exact_root_anatomy_used = {candidate['exact_root_anatomy_used']}")
        lines.append(f"fully_factored_target = {candidate['fully_factored_target']}")
        lines.append(f"residual_modeling_required = {candidate['residual_modeling_required']}")
        lines.append(f"known_branch_count = {candidate['known_branch_count']}")
        lines.append(f"modeled_branch_count = {candidate['modeled_branch_count']}")
        lines.append(f"modeled_shapes = {candidate['modeled_shapes']}")
        lines.append(f"candidate_root_children = {candidate['candidate_root_children']}")
        lines.append(f"candidate_root_generator = {candidate['candidate_root_generator']}")
        lines.append(
            f"known_root_generator_lower_bound = {candidate['known_root_generator_lower_bound']}"
        )
        lines.append(
            f"generator_matches_known_lower_bound = {candidate['generator_matches_known_lower_bound']}"
        )
        lines.append(
            f"generator_meets_known_lower_bound = {candidate['generator_meets_known_lower_bound']}"
        )
        if "exact_root_generator_from_bridge" in candidate:
            lines.append(
                f"exact_root_generator_from_bridge = {candidate['exact_root_generator_from_bridge']}"
            )
            lines.append(
                "generator_matches_exact_root_generator = "
                f"{candidate['generator_matches_exact_root_generator']}"
            )
        for note in candidate["notes"]:
            lines.append(f"note: {note}")
        lines.append("")

    return "\n".join(lines).rstrip()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build and rank one or more hybrid PET candidates from a bridge payload."
    )
    parser.add_argument("bridge", help="Path to pet_hybrid_bridge JSON payload")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    try:
        bridge = load_bridge(Path(args.bridge))
        report = build_candidates(bridge)

        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print(render_human(report))

        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
