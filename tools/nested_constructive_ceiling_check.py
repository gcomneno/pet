#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pet.core import encode, decode, shape_generator
from tools.prune_absorption_check import (
    build_rewrites,
    apply_rewrite_safe,
    get_subtree_safe,
    child_generators,
    is_prefix,
    rewrite_applicable,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Bounded checker for local ceiling admissibility on nested "
            "constructive canonical-generator rewrites."
        )
    )
    parser.add_argument("--limit", type=int, default=200000)
    parser.add_argument("--max-pairs", type=int, default=400)
    parser.add_argument("--sample-limit", type=int, default=20)
    args = parser.parse_args()

    generators = sorted({shape_generator(n) for n in range(2, args.limit + 1)})
    pool = [1] + generators

    sampled = 0
    admissible = 0
    blocked = 0
    blocked_with_upper_violation = 0
    blocked_without_upper_violation = 0
    admissible_root_mismatches = 0

    local_classes = {}
    samples = []
    weird = []

    for root_g in generators:
        if sampled >= args.max_pairs:
            break

        root_tree = encode(root_g)
        rewrites0 = build_rewrites(root_tree, pool)

        for a in rewrites0:
            if sampled >= args.max_pairs:
                break

            if a["new_child_g"] <= a["old_child_g"]:
                continue

            tree_a = apply_rewrite_safe(root_tree, a)
            if tree_a is None:
                continue

            rewrites1 = build_rewrites(tree_a, pool)

            for b in rewrites1:
                if sampled >= args.max_pairs:
                    break

                if b["new_child_g"] <= b["old_child_g"]:
                    continue

                if not is_prefix(a["target_path"], b["path"]):
                    continue

                tree_ab = apply_rewrite_safe(tree_a, b)
                if tree_ab is None:
                    continue

                sampled += 1

                parent0 = get_subtree_safe(root_tree, a["path"])
                gs0 = child_generators(parent0)
                i = a["child_idx"]
                upper = gs0[i - 1] if i > 0 else None
                lower = gs0[i + 1] if i + 1 < len(gs0) else 1

                final_subtree = get_subtree_safe(tree_ab, a["target_path"])
                final_h = 1 if final_subtree is None else decode(final_subtree)

                direct = {
                    "path": a["path"],
                    "child_idx": i,
                    "target_path": a["target_path"],
                    "old_child_g": a["old_child_g"],
                    "new_child_g": final_h,
                }

                direct_ok = rewrite_applicable(root_tree, direct)
                tree_direct = apply_rewrite_safe(root_tree, direct) if direct_ok else None

                root_ab = decode(tree_ab)
                root_direct = decode(tree_direct) if tree_direct is not None else None

                upper_violation = upper is not None and final_h > upper

                key = (tuple(gs0), i, final_h)
                rec = local_classes.setdefault(
                    key, {"ok": 0, "blocked": 0, "roots": []}
                )
                if direct_ok:
                    rec["ok"] += 1
                    admissible += 1
                    if root_direct != root_ab:
                        admissible_root_mismatches += 1
                        if len(weird) < 10:
                            weird.append(
                                {
                                    "kind": "admissible_mismatch",
                                    "root": root_g,
                                    "parent_gs": gs0,
                                    "slot": i,
                                    "upper": upper,
                                    "lower": lower,
                                    "a_target": a["target_path"],
                                    "a_move": (a["old_child_g"], a["new_child_g"]),
                                    "b_path": b["path"],
                                    "b_target": b["target_path"],
                                    "b_move": (b["old_child_g"], b["new_child_g"]),
                                    "final_h": final_h,
                                    "root_ab": root_ab,
                                    "root_direct": root_direct,
                                }
                            )
                else:
                    rec["blocked"] += 1
                    blocked += 1
                    if upper_violation:
                        blocked_with_upper_violation += 1
                    else:
                        blocked_without_upper_violation += 1
                        if len(weird) < 10:
                            weird.append(
                                {
                                    "kind": "blocked_without_upper_violation",
                                    "root": root_g,
                                    "parent_gs": gs0,
                                    "slot": i,
                                    "upper": upper,
                                    "lower": lower,
                                    "a_target": a["target_path"],
                                    "a_move": (a["old_child_g"], a["new_child_g"]),
                                    "b_path": b["path"],
                                    "b_target": b["target_path"],
                                    "b_move": (b["old_child_g"], b["new_child_g"]),
                                    "final_h": final_h,
                                }
                            )

                if len(rec["roots"]) < 6:
                    rec["roots"].append(root_g)

                if len(samples) < args.sample_limit:
                    samples.append(
                        {
                            "root": root_g,
                            "parent_gs": gs0,
                            "slot": i,
                            "upper": upper,
                            "lower": lower,
                            "a_target": a["target_path"],
                            "a_move": (a["old_child_g"], a["new_child_g"]),
                            "b_path": b["path"],
                            "b_target": b["target_path"],
                            "b_move": (b["old_child_g"], b["new_child_g"]),
                            "final_h": final_h,
                            "direct_ok": direct_ok,
                            "upper_violation": upper_violation,
                        }
                    )

    mixed_local_classes = [
        (key, rec)
        for key, rec in local_classes.items()
        if rec["ok"] and rec["blocked"]
    ]

    print(f"limit = {args.limit}")
    print(f"canonical_generators = {len(generators)}")
    print(f"sampled_nested_constructive_pairs = {sampled}")
    print(f"admissible_direct_substitution = {admissible}")
    print(f"blocked_direct_substitution = {blocked}")
    print(f"blocked_with_upper_violation = {blocked_with_upper_violation}")
    print(f"blocked_without_upper_violation = {blocked_without_upper_violation}")
    print(f"admissible_root_mismatches = {admissible_root_mismatches}")
    print(f"local_classes = {len(local_classes)}")
    print(f"mixed_local_classes = {len(mixed_local_classes)}")
    print()

    print("sample nested constructive pairs:")
    for s in samples:
        print(
            f"root={s['root']} "
            f"parent_gs={s['parent_gs']} slot={s['slot']} "
            f"upper={s['upper']} lower={s['lower']} "
            f"A@{s['a_target']} {s['a_move'][0]}->{s['a_move'][1]} "
            f"Bpath={s['b_path']} "
            f"B@{s['b_target']} {s['b_move'][0]}->{s['b_move'][1]} "
            f"final_h={s['final_h']} "
            f"direct_ok={s['direct_ok']} upper_violation={s['upper_violation']}"
        )

    print()
    print("local classes:")
    items = sorted(
        local_classes.items(),
        key=lambda kv: (kv[1]["ok"] + kv[1]["blocked"], kv[0]),
        reverse=True,
    )
    for key, rec in items[:20]:
        parent_gs, slot, final_h = key
        print(
            f"parent_gs={list(parent_gs)} slot={slot} final_h={final_h} "
            f"ok={rec['ok']} blocked={rec['blocked']} roots={rec['roots']}"
        )

    if weird:
        print()
        print("weird cases:")
        for item in weird:
            print(item)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
