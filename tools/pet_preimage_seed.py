
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pet.core import is_prime, prime_factorization, shape_signature_dict
from tools.pet_candidate_plan import first_primes, generator_from_signature


def load_report(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError("partial-explain report must be a JSON object")
    return data


def require_field(obj: dict[str, Any], name: str) -> Any:
    if name not in obj:
        raise KeyError(f"missing required field: {name}")
    return obj[name]


def select_candidate(report: dict[str, Any], rank: int) -> dict[str, Any]:
    candidates = require_field(report, "candidates")
    if not isinstance(candidates, list):
        raise TypeError("candidates must be a list")

    for candidate in candidates:
        if candidate.get("rank") == rank:
            return candidate

    raise ValueError(f"no candidate found with rank={rank}")


def _freeze(value: Any) -> Any:
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


def _signature_counter(sigs: list[list]) -> Counter:
    return Counter(_freeze(sig) for sig in sigs)


def _constructive_plan(candidate_root_children: list[list]) -> dict[str, Any]:
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
    ordered_children = [item["signature"] for item in root_items]

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
        "candidate_root_children": ordered_children,
        "root_primes": root_primes,
        "root_exponents": root_exponents,
        "start_n": 1,
        "step_count": len(steps),
        "steps": steps,
        "seed_n": current,
    }


def _gap_summary(
    known_root_children: list[list],
    root_generator_lower_bound: int,
    exact_root_anatomy: bool,
    candidate_root_children: list[list],
    candidate_root_generator: int,
) -> dict[str, Any]:
    known_counts = _signature_counter(known_root_children)
    candidate_counts = _signature_counter(candidate_root_children)

    candidate_extends_known_children = all(
        candidate_counts[sig] >= count
        for sig, count in known_counts.items()
    )
    candidate_equals_known_children = candidate_counts == known_counts

    modeled_children_count = len(candidate_root_children) - len(known_root_children)
    if modeled_children_count < 0:
        modeled_children_count = 0

    return {
        "exact_root_anatomy_certified": exact_root_anatomy,
        "candidate_extends_known_children": candidate_extends_known_children,
        "candidate_equals_known_children": candidate_equals_known_children,
        "known_children_count": len(known_root_children),
        "candidate_children_count": len(candidate_root_children),
        "modeled_children_count": modeled_children_count,
        "root_generator_gap": candidate_root_generator - root_generator_lower_bound,
    }


def _next_new_prime(support: set[int]) -> int:
    candidate = 2
    while True:
        if candidate not in support and is_prime(candidate):
            return candidate
        candidate += 1


def expand_seed_once(seed: dict[str, Any]) -> list[dict[str, Any]]:
    seed_state = require_field(seed, "seed_state")
    source_n = require_field(seed_state, "seed_n")
    if not isinstance(source_n, int):
        raise TypeError("seed_state.seed_n must be an int")

    factors = prime_factorization(source_n)
    support = {p for p, _ in factors}

    rows: list[dict[str, Any]] = []

    q = _next_new_prime(support)
    new_n = source_n * q
    rows.append(
        {
            "op": "NEW",
            "label": f"NEW(x{q})",
            "source_n": source_n,
            "target_n": new_n,
            "target_generator": shape_signature_dict(new_n)["generator"],
        }
    )

    by_exp: dict[int, list[int]] = {}
    for prime, exp in factors:
        by_exp.setdefault(exp, []).append(prime)

    for exp in sorted(by_exp):
        primes = sorted(by_exp[exp])
        rep = primes[0]
        target_n = source_n * rep
        rows.append(
            {
                "op": "INC",
                "label": f"INC(p={rep},e={exp})",
                "source_n": source_n,
                "target_n": target_n,
                "target_generator": shape_signature_dict(target_n)["generator"],
            }
        )

    return rows


def expand_seed_layer(seeds: list[dict[str, Any]], max_target_n: int | None = None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    by_target: dict[int, dict[str, Any]] = {}

    for seed in seeds:
        for row in expand_seed_once(seed):
            target_n = row["target_n"]

            if max_target_n is not None and target_n > max_target_n:
                continue

            if target_n not in by_target:
                merged = dict(row)
                merged["source_count"] = 1
                merged["source_ns"] = [row["source_n"]]
                by_target[target_n] = merged
                rows.append(merged)
                continue

            merged = by_target[target_n]
            merged["source_count"] += 1

            source_n = row["source_n"]
            if source_n not in merged["source_ns"]:
                merged["source_ns"].append(source_n)
                merged["source_ns"].sort()

    return rows


def advance_seed(seed: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    seed_state = require_field(seed, "seed_state")
    certified_constraints = require_field(seed, "certified_constraints")
    search_policy = require_field(seed, "search_policy")

    root_seed_n = require_field(seed_state, "seed_n")
    parent_n = require_field(seed_state, "seed_n")
    current_n = require_field(row, "target_n")
    current_generator = require_field(row, "target_generator")
    last_op = require_field(row, "op")
    last_label = require_field(row, "label")

    if not isinstance(root_seed_n, int):
        raise TypeError("seed_state.seed_n must be an int")
    if not isinstance(parent_n, int):
        raise TypeError("seed_state.seed_n must be an int")
    if not isinstance(current_n, int):
        raise TypeError("row.target_n must be an int")
    if not isinstance(current_generator, int):
        raise TypeError("row.target_generator must be an int")
    if not isinstance(last_op, str):
        raise TypeError("row.op must be a string")
    if not isinstance(last_label, str):
        raise TypeError("row.label must be a string")

    return {
        "schema": "pet-preimage-search-node-v0",
        "source_n": seed["source_n"],
        "root_seed_n": root_seed_n,
        "parent_n": parent_n,
        "current_n": current_n,
        "current_generator": current_generator,
        "depth": 1,
        "last_op": last_op,
        "last_label": last_label,
        "path": [last_label],
        "certified_constraints": certified_constraints,
        "search_policy": search_policy,
    }


def expand_node_once(node: dict[str, Any]) -> list[dict[str, Any]]:
    source_n = require_field(node, "current_n")
    if not isinstance(source_n, int):
        raise TypeError("node.current_n must be an int")

    factors = prime_factorization(source_n)
    support = {p for p, _ in factors}

    rows: list[dict[str, Any]] = []

    q = _next_new_prime(support)
    new_n = source_n * q
    rows.append(
        {
            "op": "NEW",
            "label": f"NEW(x{q})",
            "source_n": source_n,
            "target_n": new_n,
            "target_generator": shape_signature_dict(new_n)["generator"],
        }
    )

    by_exp: dict[int, list[int]] = {}
    for prime, exp in factors:
        by_exp.setdefault(exp, []).append(prime)

    for exp in sorted(by_exp):
        primes = sorted(by_exp[exp])
        rep = primes[0]
        target_n = source_n * rep
        rows.append(
            {
                "op": "INC",
                "label": f"INC(p={rep},e={exp})",
                "source_n": source_n,
                "target_n": target_n,
                "target_generator": shape_signature_dict(target_n)["generator"],
            }
        )

    return rows


def advance_node(node: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    certified_constraints = require_field(node, "certified_constraints")
    search_policy = require_field(node, "search_policy")

    root_seed_n = require_field(node, "root_seed_n")
    parent_n = require_field(node, "current_n")
    current_n = require_field(row, "target_n")
    current_generator = require_field(row, "target_generator")
    last_op = require_field(row, "op")
    last_label = require_field(row, "label")
    depth = require_field(node, "depth")
    path = require_field(node, "path")

    if not isinstance(root_seed_n, int):
        raise TypeError("node.root_seed_n must be an int")
    if not isinstance(parent_n, int):
        raise TypeError("node.current_n must be an int")
    if not isinstance(current_n, int):
        raise TypeError("row.target_n must be an int")
    if not isinstance(current_generator, int):
        raise TypeError("row.target_generator must be an int")
    if not isinstance(last_op, str):
        raise TypeError("row.op must be a string")
    if not isinstance(last_label, str):
        raise TypeError("row.label must be a string")
    if not isinstance(depth, int):
        raise TypeError("node.depth must be an int")
    if not isinstance(path, list):
        raise TypeError("node.path must be a list")

    return {
        "schema": "pet-preimage-search-node-v0",
        "source_n": node["source_n"],
        "root_seed_n": root_seed_n,
        "parent_n": parent_n,
        "current_n": current_n,
        "current_generator": current_generator,
        "depth": depth + 1,
        "last_op": last_op,
        "last_label": last_label,
        "path": list(path) + [last_label],
        "certified_constraints": certified_constraints,
        "search_policy": search_policy,
    }


def expand_node_layer(
    nodes: list[dict[str, Any]],
    max_target_n: int | None = None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    by_target: dict[int, dict[str, Any]] = {}

    for node in nodes:
        parent_n = require_field(node, "current_n")
        parent_depth = require_field(node, "depth")
        parent_path = require_field(node, "path")

        if not isinstance(parent_n, int):
            raise TypeError("node.current_n must be an int")
        if not isinstance(parent_depth, int):
            raise TypeError("node.depth must be an int")
        if not isinstance(parent_path, list):
            raise TypeError("node.path must be a list")

        for row in expand_node_once(node):
            target_n = row["target_n"]

            if max_target_n is not None and target_n > max_target_n:
                continue

            parent_entry = {
                "parent_n": parent_n,
                "parent_depth": parent_depth,
                "parent_path": list(parent_path),
                "via_label": row["label"],
            }

            if target_n not in by_target:
                merged = dict(row)
                merged["source_count"] = 1
                merged["source_ns"] = [row["source_n"]]
                merged["parent_entries"] = [parent_entry]
                by_target[target_n] = merged
                rows.append(merged)
                continue

            merged = by_target[target_n]
            merged["source_count"] += 1

            source_n = row["source_n"]
            if source_n not in merged["source_ns"]:
                merged["source_ns"].append(source_n)
                merged["source_ns"].sort()

            merged["parent_entries"].append(parent_entry)

    return rows


def advance_layer_row(
    seed: dict[str, Any],
    row: dict[str, Any],
    parent_index: int = 0,
) -> dict[str, Any]:
    certified_constraints = require_field(seed, "certified_constraints")
    search_policy = require_field(seed, "search_policy")
    seed_state = require_field(seed, "seed_state")

    root_seed_n = require_field(seed_state, "seed_n")
    current_n = require_field(row, "target_n")
    current_generator = require_field(row, "target_generator")
    parent_entries = require_field(row, "parent_entries")

    if not isinstance(root_seed_n, int):
        raise TypeError("seed_state.seed_n must be an int")
    if not isinstance(current_n, int):
        raise TypeError("row.target_n must be an int")
    if not isinstance(current_generator, int):
        raise TypeError("row.target_generator must be an int")
    if not isinstance(parent_entries, list):
        raise TypeError("row.parent_entries must be a list")
    if not (0 <= parent_index < len(parent_entries)):
        raise IndexError("parent_index out of range")

    parent_entry = parent_entries[parent_index]
    parent_n = require_field(parent_entry, "parent_n")
    parent_depth = require_field(parent_entry, "parent_depth")
    parent_path = require_field(parent_entry, "parent_path")
    via_label = require_field(parent_entry, "via_label")

    if not isinstance(parent_n, int):
        raise TypeError("parent_entry.parent_n must be an int")
    if not isinstance(parent_depth, int):
        raise TypeError("parent_entry.parent_depth must be an int")
    if not isinstance(parent_path, list):
        raise TypeError("parent_entry.parent_path must be a list")
    if not isinstance(via_label, str):
        raise TypeError("parent_entry.via_label must be a string")

    last_label = via_label
    last_op = via_label.split("(", 1)[0]

    return {
        "schema": "pet-preimage-search-node-v0",
        "source_n": seed["source_n"],
        "root_seed_n": root_seed_n,
        "parent_n": parent_n,
        "current_n": current_n,
        "current_generator": current_generator,
        "depth": parent_depth + 1,
        "last_op": last_op,
        "last_label": last_label,
        "path": list(parent_path) + [last_label],
        "certified_constraints": certified_constraints,
        "search_policy": search_policy,
    }

def advance_node_layer_rows(
    seed: dict[str, Any],
    layer_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not isinstance(layer_rows, list):
        raise TypeError("layer_rows must be a list")

    out: list[dict[str, Any]] = []

    for row in layer_rows:
        parent_entries = require_field(row, "parent_entries")
        if not isinstance(parent_entries, list):
            raise TypeError("row.parent_entries must be a list")

        for parent_index in range(len(parent_entries)):
            out.append(advance_layer_row(seed, row, parent_index=parent_index))

    return out


def search_step(
    seed: dict[str, Any],
    nodes: list[dict[str, Any]],
    max_target_n: int | None = None,
) -> list[dict[str, Any]]:
    layer_rows = expand_node_layer(nodes, max_target_n=max_target_n)
    return advance_node_layer_rows(seed, layer_rows)


def build_seed(report: dict[str, Any], rank: int = 1) -> dict[str, Any]:
    source_n = require_field(report, "n")
    source_schedule = require_field(report, "schedule")
    probe = require_field(report, "probe")
    candidate = select_candidate(report, rank)

    if not isinstance(source_schedule, list):
        raise TypeError("schedule must be a list")
    if not isinstance(probe, dict):
        raise TypeError("probe must be an object")
    if not isinstance(candidate, dict):
        raise TypeError("candidate must be an object")

    candidate_root_children = require_field(candidate, "candidate_root_children")
    candidate_root_generator = require_field(candidate, "candidate_root_generator")

    if not isinstance(candidate_root_children, list):
        raise TypeError("candidate_root_children must be a list")
    if not isinstance(candidate_root_generator, int):
        raise TypeError("candidate_root_generator must be an int")

    plan = _constructive_plan(candidate_root_children)

    return {
        "schema": "pet-preimage-seed-v0",
        "source_n": source_n,
        "source_schedule": source_schedule,
        "certified_constraints": {
            "exact_root_anatomy": probe["exact_root_anatomy"],
            "known_root_children": probe["known_root_children"],
            "known_root_generator_lower_bound": probe["known_root_generator_lower_bound"],
            "root_generator_lower_bound": probe["root_generator_lower_bound"],
            "residual_status": probe["residual_info"]["status"],
            "residual": probe["residual"],
            "stop_reason": probe["stop_reason"],
            "closure_kind": probe["closure_kind"],
            "fully_factored": probe["fully_factored"],
        },
        "hypothesized_candidate": {
            "rank": candidate["rank"],
            "candidate_kind": candidate["candidate_kind"],
            "candidate_root_children": candidate_root_children,
            "candidate_root_generator": candidate_root_generator,
            "score": candidate.get("score"),
            "score_terms": candidate.get("score_terms"),
            "notes": candidate.get("notes"),
        },
        "seed_state": {
            "start_n": plan["start_n"],
            "seed_n": plan["seed_n"],
            "candidate_root_generator": candidate_root_generator,
            "matches_candidate_root_generator": (
                plan["seed_n"] == candidate_root_generator
            ),
            "candidate_root_children": plan["candidate_root_children"],
            "root_primes": plan["root_primes"],
            "root_exponents": plan["root_exponents"],
            "step_count": plan["step_count"],
            "constructive_plan": {
                "start_n": plan["start_n"],
                "steps": plan["steps"],
            },
        },
        "certified_vs_hypothesis_gap": _gap_summary(
            known_root_children=probe["known_root_children"],
            root_generator_lower_bound=probe["root_generator_lower_bound"],
            exact_root_anatomy=probe["exact_root_anatomy"],
            candidate_root_children=candidate_root_children,
            candidate_root_generator=candidate_root_generator,
        ),
        "search_policy": {
            "allowed_forward_ops": ["NEW", "INC"],
            "forbidden_ops": ["DROP", "DEC"],
            "seed_semantics": (
                "seed_n is the minimal canonical compatible generator implied by the selected candidate"
            ),
            "target_semantics": (
                "search explores plausible forward preimages compatible with the certified Partial-PET constraints"
            ),
        },
    }


def render_human(seed: dict[str, Any]) -> str:
    lines: list[str] = []

    lines.append(f"schema = {seed['schema']}")
    lines.append(f"source_n = {seed['source_n']}")
    lines.append(f"source_schedule = {seed['source_schedule']}")

    certified = seed["certified_constraints"]
    lines.append("certified_constraints:")
    for key in (
        "exact_root_anatomy",
        "known_root_children",
        "known_root_generator_lower_bound",
        "root_generator_lower_bound",
        "residual_status",
        "residual",
        "stop_reason",
        "closure_kind",
        "fully_factored",
    ):
        lines.append(f"  {key} = {certified[key]}")

    hypo = seed["hypothesized_candidate"]
    lines.append("hypothesized_candidate:")
    for key in (
        "rank",
        "candidate_kind",
        "candidate_root_generator",
        "candidate_root_children",
    ):
        lines.append(f"  {key} = {hypo[key]}")

    state = seed["seed_state"]
    lines.append("seed_state:")
    for key in (
        "start_n",
        "seed_n",
        "candidate_root_generator",
        "matches_candidate_root_generator",
        "candidate_root_children",
        "root_primes",
        "root_exponents",
        "step_count",
    ):
        lines.append(f"  {key} = {state[key]}")

    gap = seed["certified_vs_hypothesis_gap"]
    lines.append("certified_vs_hypothesis_gap:")
    for key in (
        "exact_root_anatomy_certified",
        "candidate_extends_known_children",
        "candidate_equals_known_children",
        "known_children_count",
        "candidate_children_count",
        "modeled_children_count",
        "root_generator_gap",
    ):
        lines.append(f"  {key} = {gap[key]}")

    policy = seed["search_policy"]
    lines.append("search_policy:")
    lines.append(f"  allowed_forward_ops = {policy['allowed_forward_ops']}")
    lines.append(f"  forbidden_ops = {policy['forbidden_ops']}")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a preimage-search seed from a partial-explain JSON report."
    )
    parser.add_argument("report", help="Path to partial-explain JSON report")
    parser.add_argument(
        "--rank",
        type=int,
        default=1,
        help="Candidate rank to seed from (default: 1)",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    try:
        report = load_report(Path(args.report))
        seed = build_seed(report, rank=args.rank)

        if args.json:
            print(json.dumps(seed, ensure_ascii=False, indent=2))
        else:
            print(render_human(seed))

        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
