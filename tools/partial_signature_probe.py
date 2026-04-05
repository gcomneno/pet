#!/usr/bin/env python3
from __future__ import annotations

import sys
import time
import argparse
import json
from collections import Counter
from math import prod
from typing import Any

from sympy import factorint, isprime
from sympy.ntheory.factor_ import perfect_power, pollard_rho

from pet.core import shape_signature_dict


SMALL_RESIDUAL_EXACT_LIMIT = 10**8


def _trace(msg: str) -> None:
    print(f"[trace] {msg}", file=sys.stderr, flush=True)


def _freeze(x: Any):
    if isinstance(x, list):
        return tuple(_freeze(y) for y in x)
    return x


def _canonicalize_signatures(sigs: list[list]) -> list[list]:
    return sorted(sigs, key=_freeze)


def _signature_multiset(sigs: list[list]) -> Counter:
    return Counter(_freeze(sig) for sig in _canonicalize_signatures(sigs))


def _multiset_inclusion(left: list[list], right: list[list]) -> bool:
    left_counts = _signature_multiset(left)
    right_counts = _signature_multiset(right)
    return all(count <= right_counts.get(sig, 0) for sig, count in left_counts.items())


def _first_primes(count: int) -> list[int]:
    primes: list[int] = []
    candidate = 2

    while len(primes) < count:
        if isprime(candidate):
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


def _factorint_bounded(n: int, limit: int) -> dict[int, int]:
    raw = factorint(n, limit=limit)
    return {int(k): int(v) for k, v in raw.items()}


def _factor_small_residual_exact(
    residual: int,
) -> tuple[dict[int, int], list[tuple[int, int]], int] | None:
    if residual <= 1 or residual > SMALL_RESIDUAL_EXACT_LIMIT:
        return None

    raw = _factorint_bounded(residual, SMALL_RESIDUAL_EXACT_LIMIT)
    stage_known, residual_after = _split_known_and_residual(raw)
    if residual_after != 1:
        return None

    return raw, stage_known, residual_after


def _split_known_and_residual(factors: dict[int, int]) -> tuple[list[tuple[int, int]], int]:
    known: list[tuple[int, int]] = []
    residual_parts: list[int] = []

    for base, exp in sorted(factors.items()):
        if isprime(base):
            known.append((base, exp))
        else:
            residual_parts.append(base ** exp)

    residual = prod(residual_parts) if residual_parts else 1
    return known, residual


def _merge_factor_lists(acc: dict[int, int], found: list[tuple[int, int]]) -> None:
    for p, e in found:
        acc[p] = acc.get(p, 0) + e


def _extract_prime_power(n: int, p: int) -> tuple[int, int]:
    exp = 0
    residual = n
    while residual % p == 0:
        residual //= p
        exp += 1
    return exp, residual


def _rho_find_prime_factor(n: int, depth: int = 0) -> int | None:
    if n < 2:
        return None
    if isprime(n):
        return int(n)
    if depth > 4:
        return None

    # Guardrail: Pollard Rho non è una bacchetta magica sui residui enormi.
    # Sopra questa soglia preferiamo fermarci presto anziché inchiodarci.
    if n.bit_length() > 256:
        return None

    seeds = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    a_values = [1, 3, 5, 7, 11, 13, 17, 19]
    s_values = [2, 3, 5, 7]

    for seed in seeds:
        for a in a_values:
            for s in s_values:
                try:
                    candidate = pollard_rho(
                        n,
                        s=s,
                        a=a,
                        seed=seed,
                        retries=0,
                        max_steps=5000,
                    )
                except Exception:
                    candidate = None

                if not candidate:
                    continue

                candidate = int(candidate)
                if candidate in (1, n):
                    continue

                if isprime(candidate):
                    return candidate

                inner = _rho_find_prime_factor(candidate, depth + 1)
                if inner and 1 < inner < n:
                    return inner

                other = n // candidate
                if other not in (1, n):
                    inner = _rho_find_prime_factor(other, depth + 1)
                    if inner and 1 < inner < n:
                        return inner

    return None


def _exp_signature_data(exp: int) -> dict[str, Any]:
    if exp < 1:
        raise ValueError("exponent must be >= 1")

    if exp == 1:
        return {
            "generator": 1,
            "signature": [],
        }

    data = shape_signature_dict(exp)
    return {
        "generator": data["generator"],
        "signature": data["signature"],
    }


def _known_factor_items(known_factor_map: dict[int, int]) -> list[dict[str, Any]]:
    items = []
    for prime, exp in sorted(known_factor_map.items()):
        exp_sig_data = _exp_signature_data(exp)
        items.append(
            {
                "prime": prime,
                "exp": exp,
                "exp_generator": exp_sig_data["generator"],
                "exp_signature": exp_sig_data["signature"],
            }
        )
    return items


def _known_root_children(known_factor_map: dict[int, int]) -> list[list]:
    children = []
    for item in _known_factor_items(known_factor_map):
        children.append(item["exp_signature"])
    return _canonicalize_signatures(children)


def _classify_residual(residual: int) -> dict[str, Any]:
    if residual == 1:
        return {
            "status": "unit",
            "root_children_lower_bound": 0,
            "exact_root_children": [],
            "notes": [],
        }

    if isprime(residual):
        return {
            "status": "prime-by-sympy",
            "root_children_lower_bound": 1,
            "exact_root_children": [[]],
            "notes": ["residual behaves like one prime factor of exponent 1"],
        }

    pp = perfect_power(residual)
    if pp:
        base, exp = int(pp[0]), int(pp[1])

        if isprime(base):
            exp_sig = _exp_signature_data(exp)
            return {
                "status": "prime-power-by-sympy",
                "root_children_lower_bound": 1,
                "exact_root_children": [exp_sig["signature"]],
                "prime_power_base": base,
                "prime_power_exp": exp,
                "notes": [
                    "residual behaves like one prime factor with exponent > 1"
                ],
            }

        return {
            "status": "perfect-power-composite-base",
            "root_children_lower_bound": 2,
            "exact_root_children": None,
            "perfect_power_base": base,
            "perfect_power_exp": exp,
            "notes": [
                "residual is a perfect power, but its base is composite",
                "root contribution is not yet exact",
            ],
        }

    return {
        "status": "composite-non-prime-power",
        "root_children_lower_bound": 2,
        "exact_root_children": None,
        "notes": [
            "residual is composite and not a prime power",
            "so it contributes at least two root children",
        ],
    }


def _residual_status_refines_v0(status2: str, status1: str) -> bool:
    if status2 == status1:
        return True
    return (
        status2 == "perfect-power-composite-base"
        and status1 == "composite-non-prime-power"
    )


def _residual_compatible_with_status_v0(
    exact_children: list[list],
    known_children: list[list],
    status: str,
) -> bool:
    exact_counts = _signature_multiset(exact_children)
    known_counts = _signature_multiset(known_children)
    residual_size = sum(
        exact_counts.get(sig, 0) - known_counts.get(sig, 0) for sig in exact_counts
    )

    if status == "unit":
        return residual_size == 0
    if status == "prime-by-sympy":
        return residual_size == 1
    if status == "prime-power-by-sympy":
        return residual_size == 1
    if status == "composite-non-prime-power":
        return residual_size >= 2
    if status == "perfect-power-composite-base":
        return residual_size >= 2
    return False


def refines_v0(p2: dict[str, Any], p1: dict[str, Any]) -> bool:
    k1 = _canonicalize_signatures(p1["known_root_children"])
    k2 = _canonicalize_signatures(p2["known_root_children"])

    if not _multiset_inclusion(k1, k2):
        return False

    if p2["known_root_generator_lower_bound"] < p1["known_root_generator_lower_bound"]:
        return False

    if p2["root_generator_lower_bound"] < p1["root_generator_lower_bound"]:
        return False

    exact1 = bool(p1["exact_root_anatomy"])
    exact2 = bool(p2["exact_root_anatomy"])

    if exact1:
        if not exact2:
            return False
        e1 = _canonicalize_signatures(p1["exact_root_children"] or [])
        e2 = _canonicalize_signatures(p2["exact_root_children"] or [])
        return e2 == e1

    status1 = p1["residual_info"]["status"]

    if not exact2:
        status2 = p2["residual_info"]["status"]
        return _residual_status_refines_v0(status2, status1)

    e2 = _canonicalize_signatures(p2["exact_root_children"] or [])
    if not _multiset_inclusion(k1, e2):
        return False

    return _residual_compatible_with_status_v0(e2, k1, status1)


def _last_split_kind_from_stage(
    stage_source: str,
    stage_raw: dict[int, int],
    stage_known: list[tuple[int, int]],
    residual_after: int,
) -> str:
    if not stage_known and residual_after != 1:
        return "no-progress"

    if stage_source == "pollard-rho":
        if len(stage_known) == 1 and stage_known[0][1] == 1:
            return "rho-prime-extraction"
        if len(stage_known) == 1 and stage_known[0][1] > 1:
            return "rho-prime-power-extraction"
        return "rho-split"

    if len(stage_raw) == 1:
        base, exp = next(iter(stage_raw.items()))
        if isprime(base):
            if exp == 1:
                return "single-prime"
            return "single-prime-power"
        return "single-composite-fragment"

    return "multi-prime-split"


def _closure_kind_from_stage(
    stage_raw: dict[int, int],
    stage_known: list[tuple[int, int]],
    residual_after: int,
) -> str | None:
    residual_info = _classify_residual(residual_after)
    status = residual_info["status"]

    if status == "unit":
        return "unit"
    if status == "prime-by-sympy":
        return "prime-residue"
    if status == "prime-power-by-sympy":
        return "prime-power-residue"

    return None


def _stop_reason_from_residual(residual: int, *, budget_exhausted: bool) -> str:
    info = _classify_residual(residual)
    status = info["status"]

    if status == "unit":
        return "closed-unit"
    if status == "prime-by-sympy":
        return "closed-prime-residue"
    if status == "prime-power-by-sympy":
        return "closed-prime-power-residue"
    if budget_exhausted:
        return "budget-exhausted-composite-unknown"
    return "stalled-composite-unknown"


def _residual_lower_bound_children(residual_info: dict[str, Any]) -> list[list]:
    if residual_info["exact_root_children"] is not None:
        return residual_info["exact_root_children"]
    return [[] for _ in range(residual_info["root_children_lower_bound"])]


def _factor_step(
    residual_before: int,
    limit: int,
    *,
    allow_pollard_rho: bool = True,
) -> tuple[str, dict[int, int], list[tuple[int, int]], int]:
    _trace(
        f"factor_step:start digits={len(str(residual_before))} "
        f"bits={residual_before.bit_length()} limit={limit}"
    )

    t0 = time.perf_counter()
    stage_raw = _factorint_bounded(residual_before, limit)
    t1 = time.perf_counter()
    _trace(
        f"factorint:done elapsed={t1-t0:.3f}s raw_keys={list(stage_raw.keys())[:5]} "
        f"raw_len={len(stage_raw)}"
    )

    stage_known, residual_after = _split_known_and_residual(stage_raw)

    if stage_known or residual_after != residual_before:
        _trace(
            f"factor_step:progress source=factorint known={stage_known} "
            f"residual_changed={residual_after != residual_before}"
        )
        return "factorint", stage_raw, stage_known, residual_after

    residual_info = _classify_residual(residual_before)
    _trace(f"factor_step:no-progress residual_status={residual_info['status']}")

    if residual_info["status"] not in {
        "composite-non-prime-power",
        "perfect-power-composite-base",
    }:
        return "factorint", stage_raw, stage_known, residual_after

    if not allow_pollard_rho:
        return "factorint", stage_raw, stage_known, residual_after

    _trace("pollard_rho:start")
    t0 = time.perf_counter()
    prime_factor = _rho_find_prime_factor(residual_before)
    t1 = time.perf_counter()
    _trace(f"pollard_rho:done elapsed={t1-t0:.3f}s factor={prime_factor}")

    if prime_factor is None or prime_factor in (1, residual_before):
        return "factorint", stage_raw, stage_known, residual_after

    exp, remainder = _extract_prime_power(residual_before, prime_factor)
    rho_raw: dict[int, int] = {int(prime_factor): int(exp)}
    if remainder != 1:
        rho_raw[int(remainder)] = 1

    rho_known = [(int(prime_factor), int(exp))]
    _trace(f"pollard_rho:progress factor={prime_factor} exp={exp} remainder_digits={len(str(remainder))}")
    return "pollard-rho", rho_raw, rho_known, int(remainder)


def _make_stage(
    *,
    stage_source: str,
    limit: int,
    residual_before: int,
    stage_raw: dict[int, int],
    stage_known: list[tuple[int, int]],
    residual_after: int,
    known_factor_map: dict[int, int],
) -> dict[str, Any]:
    known_children = _known_root_children(known_factor_map)
    known_root_generator_lower_bound = _root_generator_from_children(known_children)

    residual_info = _classify_residual(residual_after)
    residual_lb_children = _residual_lower_bound_children(residual_info)

    root_generator_lower_bound = _root_generator_from_children(
        _canonicalize_signatures(known_children + residual_lb_children)
    )

    exact_root_children = None
    exact_root_generator = None
    if residual_info["exact_root_children"] is not None:
        exact_root_children = _canonicalize_signatures(
            known_children + residual_info["exact_root_children"]
        )
        exact_root_generator = _root_generator_from_children(exact_root_children)

    progress = bool(stage_known) or residual_after != residual_before
    closure_kind = _closure_kind_from_stage(stage_raw, stage_known, residual_after)
    last_split_kind = _last_split_kind_from_stage(
        stage_source, stage_raw, stage_known, residual_after
    )

    return {
        "source": stage_source,
        "limit": limit,
        "residual_before": residual_before,
        "factorint_result": stage_raw,
        "new_known_factors": [{"prime": p, "exp": e} for p, e in stage_known],
        "progress": progress,
        "closure_kind": closure_kind,
        "last_split_kind": last_split_kind,
        "known_factors_so_far": _known_factor_items(known_factor_map),
        "known_root_children_so_far": known_children,
        "known_root_generator_lower_bound": known_root_generator_lower_bound,
        "residual_after": residual_after,
        "residual_info": residual_info,
        "root_generator_lower_bound": root_generator_lower_bound,
        "exact_root_children_if_closed_now": exact_root_children,
        "exact_root_generator_if_closed_now": exact_root_generator,
    }


def _analyze_residual_recursive(
    residual: int,
    remaining_schedule: list[int],
    known_factor_map: dict[int, int],
    stages: list[dict[str, Any]],
    *,
    allow_pollard_rho: bool = True,
    allow_small_residual_exact: bool = True,
) -> tuple[int, str]:
    _trace(
        f"recurse:start digits={len(str(residual))} "
        f"schedule={remaining_schedule}"
    )    
    residual_info = _classify_residual(residual)
    if residual_info["exact_root_children"] is not None:
        return residual, _stop_reason_from_residual(residual, budget_exhausted=False)

    if not remaining_schedule:
        if allow_small_residual_exact:
            exact_small = _factor_small_residual_exact(residual)
            if exact_small is not None:
                stage_raw, stage_known, residual_after = exact_small
                if stage_known:
                    _merge_factor_lists(known_factor_map, stage_known)

                stage = _make_stage(
                    stage_source="small-residual-exact",
                    limit=SMALL_RESIDUAL_EXACT_LIMIT,
                    residual_before=residual,
                    stage_raw=stage_raw,
                    stage_known=stage_known,
                    residual_after=residual_after,
                    known_factor_map=known_factor_map,
                )
                stages.append(stage)
                _trace(f"recurse:stop reason={_stop_reason_from_residual(residual_after, budget_exhausted=False)}")
                return residual_after, _stop_reason_from_residual(residual_after, budget_exhausted=False)

        return residual, _stop_reason_from_residual(residual, budget_exhausted=True)

    limit = remaining_schedule[0]
    residual_before = residual
    stage_source, stage_raw, stage_known, residual_after = _factor_step(
        residual_before,
        limit,
        allow_pollard_rho=allow_pollard_rho,
    )

    if stage_known:
        _merge_factor_lists(known_factor_map, stage_known)

    stage = _make_stage(
        stage_source=stage_source,
        limit=limit,
        residual_before=residual_before,
        stage_raw=stage_raw,
        stage_known=stage_known,
        residual_after=residual_after,
        known_factor_map=known_factor_map,
    )
    stages.append(stage)

    if stage["exact_root_children_if_closed_now"] is not None:
        _trace(f"recurse:stop reason={_stop_reason_from_residual(residual, budget_exhausted=False)}")
        return residual_after, _stop_reason_from_residual(residual_after, budget_exhausted=False)

    if not stage["progress"]:
        _trace(f"recurse:stop reason={_stop_reason_from_residual(residual, budget_exhausted=False)}")
        if len(remaining_schedule) == 1:
            return residual_after, _stop_reason_from_residual(residual_after, budget_exhausted=False)
        return _analyze_residual_recursive(
            residual_after,
            remaining_schedule[1:],
            known_factor_map,
            stages,
            allow_pollard_rho=allow_pollard_rho,
            allow_small_residual_exact=allow_small_residual_exact,
        )

    _trace(f"recurse:stop reason={_stop_reason_from_residual(residual, budget_exhausted=False)}")
    return _analyze_residual_recursive(
        residual_after,
        remaining_schedule[1:],
        known_factor_map,
        stages,
        allow_pollard_rho=allow_pollard_rho,
        allow_small_residual_exact=allow_small_residual_exact,
    )


def build_report(
    n: int,
    schedule: list[int],
    *,
    allow_pollard_rho: bool = True,
    allow_small_residual_exact: bool = True,
) -> dict[str, Any]:
    known_factor_map: dict[int, int] = {}
    stages: list[dict[str, Any]] = []

    residual, stop_reason = _analyze_residual_recursive(
        residual=n,
        remaining_schedule=schedule,
        known_factor_map=known_factor_map,
        stages=stages,
        allow_pollard_rho=allow_pollard_rho,
        allow_small_residual_exact=allow_small_residual_exact,
    )

    final_known_children = _known_root_children(known_factor_map)
    final_known_root_generator_lower_bound = _root_generator_from_children(final_known_children)
    final_residual_info = _classify_residual(residual)
    final_residual_lb_children = _residual_lower_bound_children(final_residual_info)
    final_root_generator_lower_bound = _root_generator_from_children(
        _canonicalize_signatures(final_known_children + final_residual_lb_children)
    )

    exact_root_children = None
    exact_root_generator = None
    if final_residual_info["exact_root_children"] is not None:
        exact_root_children = _canonicalize_signatures(
            final_known_children + final_residual_info["exact_root_children"]
        )
        exact_root_generator = _root_generator_from_children(exact_root_children)

    closure_kind = None
    if exact_root_children is not None:
        status = final_residual_info["status"]
        if status == "unit":
            closure_kind = "unit"
        elif status == "prime-by-sympy":
            closure_kind = "prime-residue"
        elif status == "prime-power-by-sympy":
            closure_kind = "prime-power-residue"

    last_progress_stage_kind = None
    for stage in reversed(stages):
        if stage.get("progress"):
            last_progress_stage_kind = stage.get("last_split_kind")
            break

    return {
        "n": n,
        "schedule": schedule,
        "allow_pollard_rho": allow_pollard_rho,
        "allow_small_residual_exact": allow_small_residual_exact,
        "stages": stages,
        "stop_reason": stop_reason,
        "closure_kind": closure_kind,
        "last_progress_stage_kind": last_progress_stage_kind,
        "stalled": stop_reason == "stalled-composite-unknown",
        "rho_used": any(stage["source"] == "pollard-rho" for stage in stages),
        "known_factors": _known_factor_items(known_factor_map),
        "known_root_children": final_known_children,
        "known_root_generator_lower_bound": final_known_root_generator_lower_bound,
        "residual": residual,
        "residual_info": final_residual_info,
        "root_generator_lower_bound": final_root_generator_lower_bound,
        "exact_root_anatomy": exact_root_children is not None,
        "exact_root_children": exact_root_children,
        "exact_root_generator": exact_root_generator,
        "fully_factored": residual == 1,
    }


def render_human(report: dict[str, Any]) -> str:
    lines = []
    lines.append(f"N = {report['n']}")
    lines.append(f"schedule = {report['schedule']}")
    lines.append("")

    for i, stage in enumerate(report["stages"], start=1):
        lines.append(f"[stage {i}] source = {stage['source']} limit = {stage['limit']}")
        lines.append(f"residual_before = {stage['residual_before']}")
        lines.append(f"factorint_result = {stage['factorint_result']}")
        lines.append(f"new_known_factors = {stage['new_known_factors']}")
        lines.append(f"known_root_children_so_far = {stage['known_root_children_so_far']}")
        lines.append(
            f"known_root_generator_lower_bound = {stage['known_root_generator_lower_bound']}"
        )
        lines.append(f"residual_after = {stage['residual_after']}")
        lines.append(f"residual_status = {stage['residual_info']['status']}")
        lines.append(
            f"residual_root_children_lower_bound = "
            f"{stage['residual_info']['root_children_lower_bound']}"
        )
        lines.append(f"root_generator_lower_bound = {stage['root_generator_lower_bound']}")
        lines.append(f"last_split_kind = {stage['last_split_kind']}")

        if stage["exact_root_children_if_closed_now"] is not None:
            lines.append(
                "exact_root_children_if_closed_now = "
                f"{stage['exact_root_children_if_closed_now']}"
            )
            lines.append(
                "exact_root_generator_if_closed_now = "
                f"{stage['exact_root_generator_if_closed_now']}"
            )
            lines.append(f"closure_kind_if_closed_now = {stage['closure_kind']}")

        if stage["residual_info"].get("notes"):
            for note in stage["residual_info"]["notes"]:
                lines.append(f"note: {note}")

        lines.append("")

    lines.append(f"stop_reason = {report['stop_reason']}")
    lines.append(f"closure_kind = {report['closure_kind']}")
    lines.append(f"last_progress_stage_kind = {report['last_progress_stage_kind']}")
    lines.append(f"rho_used = {report['rho_used']}")
    lines.append(f"stalled = {report['stalled']}")
    lines.append(f"known_factors = {report['known_factors']}")
    lines.append(f"known_root_children = {report['known_root_children']}")
    lines.append(
        f"known_root_generator_lower_bound = {report['known_root_generator_lower_bound']}"
    )
    lines.append(f"residual = {report['residual']}")
    lines.append(f"residual_status = {report['residual_info']['status']}")
    lines.append(f"root_generator_lower_bound = {report['root_generator_lower_bound']}")
    lines.append(f"exact_root_anatomy = {report['exact_root_anatomy']}")
    lines.append(f"fully_factored = {report['fully_factored']}")

    if report["exact_root_children"] is not None:
        lines.append(f"exact_root_children = {report['exact_root_children']}")
        lines.append(f"exact_root_generator = {report['exact_root_generator']}")

    return "\n".join(lines)


def parse_schedule(raw: str) -> list[int]:
    parts = [x.strip() for x in raw.split(",") if x.strip()]
    if not parts:
        raise SystemExit("schedule must contain at least one positive integer")

    schedule = []
    for p in parts:
        try:
            value = int(p)
        except ValueError as exc:
            raise SystemExit(f"invalid schedule entry: {p}") from exc
        if value < 1:
            raise SystemExit("schedule entries must be >= 1")
        schedule.append(value)

    return schedule


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Recursive bounded probe for partial/certified PET root anatomy with pollard_rho fallback."
    )
    parser.add_argument("n", type=int, help="Integer to inspect")
    parser.add_argument(
        "--schedule",
        default="100,1000,10000",
        help="Comma-separated factorint limits, e.g. 100,1000,10000",
    )
    parser.add_argument(
        "--no-pollard-rho",
        action="store_true",
        help="Disable pollard-rho fallback (experimental)",
    )
    parser.add_argument(
        "--no-small-residual-exact",
        action="store_true",
        help="Disable exact closure of small residuals at exhausted schedule (experimental)",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    if args.n < 1:
        raise SystemExit("N must be >= 1")

    schedule = parse_schedule(args.schedule)
    report = build_report(
        args.n,
        schedule,
        allow_pollard_rho=not args.no_pollard_rho,
        allow_small_residual_exact=not args.no_small_residual_exact,
    )

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_human(report))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
