#!/usr/bin/env python3
from __future__ import annotations

import argparse
from fractions import Fraction
from itertools import combinations

from pet.core import decode, encode, shape_generator


def child_generators(tree):
    return [1 if exp_repr is None else decode(exp_repr) for _, exp_repr in tree]


def iter_subtree_paths(tree, prefix=()):
    for idx, (_, exp_repr) in enumerate(tree):
        if exp_repr is not None:
            path = prefix + (idx,)
            yield path
            yield from iter_subtree_paths(exp_repr, path)


def get_subtree(tree, path):
    cur = tree
    for idx in path:
        cur = cur[idx][1]
    return cur


def set_subtree(tree, path, new_subtree):
    if not path:
        return new_subtree
    idx = path[0]
    out = list(tree)
    p, exp_repr = out[idx]
    out[idx] = (p, set_subtree(exp_repr, path[1:], new_subtree))
    return out


def replace_child_generator(node_tree, child_idx, new_g):
    out = []
    for idx, (p, exp_repr) in enumerate(node_tree):
        if idx == child_idx:
            new_exp_repr = None if new_g == 1 else encode(new_g)
            out.append((p, new_exp_repr))
        else:
            out.append((p, exp_repr))
    return out


def nearest_candidates(gs, i, pool):
    old = gs[i]
    upper = gs[i - 1] if i > 0 else None
    lower = gs[i + 1] if i + 1 < len(gs) else 1

    allowed = [
        g
        for g in pool
        if g != old and g >= lower and (upper is None or g <= upper)
    ]
    if not allowed:
        return []

    smaller = [g for g in allowed if g < old]
    larger = [g for g in allowed if g > old]

    out = []
    if smaller:
        out.append(smaller[-1])
    if larger:
        out.append(larger[0])
    return out


def build_rewrites(root_tree, pool):
    rewrites = []
    for path in iter_subtree_paths(root_tree):
        node_tree = get_subtree(root_tree, path)
        gs = child_generators(node_tree)
        for child_idx in range(len(gs)):
            for new_child_g in nearest_candidates(gs, child_idx, pool):
                rewrites.append(
                    {
                        "path": path,
                        "child_idx": child_idx,
                        "target_path": path + (child_idx,),
                        "old_child_g": gs[child_idx],
                        "new_child_g": new_child_g,
                    }
                )
    return rewrites


def apply_rewrite(root_tree, rw):
    node_tree = get_subtree(root_tree, rw["path"])
    new_node_tree = replace_child_generator(node_tree, rw["child_idx"], rw["new_child_g"])
    return set_subtree(root_tree, rw["path"], new_node_tree)


def apply_rewrites(root_tree, rws):
    cur = root_tree
    for rw in rws:
        cur = apply_rewrite(cur, rw)
    return cur


def is_prefix(a, b):
    return len(a) <= len(b) and a == b[: len(a)]


def pairwise_disjoint_targets(rws):
    targets = [rw["target_path"] for rw in rws]
    for i in range(len(targets)):
        for j in range(i + 1, len(targets)):
            a = targets[i]
            b = targets[j]
            if is_prefix(a, b) or is_prefix(b, a):
                return False
    return True


def mul_prime_delta(value, prime, delta):
    value = Fraction(value, 1) if not isinstance(value, Fraction) else value
    if delta >= 0:
        return value * (prime ** delta)
    return value / (prime ** (-delta))


def predict_root_bottom_up(root_tree, rws):
    pending = {rw["target_path"]: rw["new_child_g"] for rw in rws}

    while True:
        if not pending:
            raise RuntimeError("empty pending set: no root prediction produced")

        max_depth = max(len(path) for path in pending)

        active = {
            path: new_g
            for path, new_g in pending.items()
            if len(path) == max_depth
        }
        carry = {
            path: new_g
            for path, new_g in pending.items()
            if len(path) != max_depth
        }

        grouped = {}
        for target_path, new_g in active.items():
            parent_path = target_path[:-1]
            slot = target_path[-1]
            grouped.setdefault(parent_path, []).append((slot, new_g))

        next_pending = {}

        for parent_path, items in grouped.items():
            parent_tree = root_tree if not parent_path else get_subtree(root_tree, parent_path)
            old_parent = decode(parent_tree)
            old_childs = child_generators(parent_tree)

            predicted_parent = Fraction(old_parent, 1)
            for slot, new_child_g in items:
                prime = parent_tree[slot][0]
                delta = new_child_g - old_childs[slot]
                predicted_parent = mul_prime_delta(predicted_parent, prime, delta)

            if predicted_parent.denominator != 1:
                raise RuntimeError(
                    f"non-integer predicted parent at {parent_path}: {predicted_parent}"
                )

            predicted_parent = predicted_parent.numerator

            if parent_path == ():
                if carry:
                    raise RuntimeError(
                        "root update produced while shallower pending updates still exist"
                    )
                return predicted_parent

            next_pending[parent_path] = predicted_parent

        pending = {**carry, **next_pending}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Bounded checker for PET forest aggregation on disjoint canonical-generator rewrites."
    )
    parser.add_argument("--limit", type=int, default=10000, help="scan generators up to this bound")
    parser.add_argument("--max-k", type=int, choices=[1, 2, 3], default=3, help="max size of rewrite forests")
    parser.add_argument("--sample-limit", type=int, default=15, help="number of sample predictions to print")
    args = parser.parse_args()

    generators = sorted({shape_generator(n) for n in range(2, args.limit + 1)})
    pool = [1] + generators

    checked = {1: 0, 2: 0, 3: 0}
    mismatches = []
    samples = []

    for root_g in generators:
        root_tree = encode(root_g)
        rewrites = build_rewrites(root_tree, pool)

        for k in range(1, args.max_k + 1):
            for combo in combinations(rewrites, k):
                combo = list(combo)

                if not pairwise_disjoint_targets(combo):
                    continue

                pred_root = predict_root_bottom_up(root_tree, combo)
                actual_root = decode(apply_rewrites(root_tree, combo))
                checked[k] += 1

                if len(samples) < args.sample_limit:
                    samples.append(
                        {
                            "root": root_g,
                            "k": k,
                            "targets": [rw["target_path"] for rw in combo],
                            "moves": [(rw["old_child_g"], rw["new_child_g"]) for rw in combo],
                            "pred": pred_root,
                            "actual": actual_root,
                        }
                    )

                if pred_root != actual_root and len(mismatches) < 10:
                    mismatches.append(
                        {
                            "root": root_g,
                            "k": k,
                            "targets": [rw["target_path"] for rw in combo],
                            "moves": [(rw["old_child_g"], rw["new_child_g"]) for rw in combo],
                            "pred": pred_root,
                            "actual": actual_root,
                        }
                    )

    print(f"limit = {args.limit}")
    print(f"canonical_generators = {len(generators)}")
    for k in range(1, args.max_k + 1):
        print(f"checked_k{k} = {checked[k]}")
    print(f"mismatches = {len(mismatches)}")
    print()

    print("sample forest predictions:")
    for item in samples:
        print(
            f"root={item['root']} k={item['k']} "
            f"targets={item['targets']} moves={item['moves']} "
            f"pred={item['pred']} actual={item['actual']}"
        )

    if mismatches:
        print()
        print("first mismatches:")
        for item in mismatches:
            print(item)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
