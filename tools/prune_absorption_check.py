#!/usr/bin/env python3
from __future__ import annotations

import argparse

from pet.core import decode, encode, shape_generator


def child_generators(tree):
    return [1 if exp_repr is None else decode(exp_repr) for _, exp_repr in tree]


def iter_subtree_paths(tree, prefix=()):
    for idx, (_, exp_repr) in enumerate(tree):
        if exp_repr is not None:
            path = prefix + (idx,)
            yield path
            yield from iter_subtree_paths(exp_repr, path)


def get_subtree_safe(tree, path):
    cur = tree
    for idx in path:
        if cur is None or idx < 0 or idx >= len(cur):
            return None
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
        node_tree = get_subtree_safe(root_tree, path)
        gs = child_generators(node_tree)
        for child_idx in range(len(gs)):
            cands = nearest_candidates(gs, child_idx, pool)
            if cands:
                rewrites.append(
                    {
                        "path": path,
                        "child_idx": child_idx,
                        "target_path": path + (child_idx,),
                        "old_child_g": gs[child_idx],
                        "new_child_g": cands[0],
                    }
                )
    return rewrites


def is_prefix(a, b):
    return len(a) <= len(b) and a == b[: len(a)]


def rewrite_applicable(tree, rw):
    node = get_subtree_safe(tree, rw["path"])
    if node is None:
        return False
    if rw["child_idx"] < 0 or rw["child_idx"] >= len(node):
        return False

    gs = child_generators(node)
    i = rw["child_idx"]
    new_g = rw["new_child_g"]

    upper = gs[i - 1] if i > 0 else None
    lower = gs[i + 1] if i + 1 < len(gs) else 1

    return (
        new_g != gs[i]
        and new_g >= lower
        and (upper is None or new_g <= upper)
    )


def apply_rewrite_safe(tree, rw):
    if not rewrite_applicable(tree, rw):
        return None
    node = get_subtree_safe(tree, rw["path"])
    new_node = replace_child_generator(node, rw["child_idx"], rw["new_child_g"])
    return set_subtree(tree, rw["path"], new_node)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Bounded checker for prune absorption on nested canonical-generator rewrites."
    )
    parser.add_argument("--limit", type=int, default=1000000)
    parser.add_argument("--max-pairs", type=int, default=200)
    parser.add_argument("--sample-limit", type=int, default=15)
    args = parser.parse_args()

    generators = sorted({shape_generator(n) for n in range(2, args.limit + 1)})
    pool = [1] + generators

    sampled = 0
    da_valid = 0
    ad_invalid = 0
    absorbed = 0
    mismatches = []
    samples = []

    for root_g in generators:
        if sampled >= args.max_pairs:
            break

        root_tree = encode(root_g)
        rewrites = build_rewrites(root_tree, pool)
        prune_ancestors = [rw for rw in rewrites if rw["new_child_g"] == 1]

        for a in prune_ancestors:
            if sampled >= args.max_pairs:
                break

            for b in rewrites:
                if sampled >= args.max_pairs:
                    break

                if a is b:
                    continue
                if not is_prefix(a["target_path"], b["target_path"]):
                    continue
                if a["target_path"] == b["target_path"]:
                    continue

                sampled += 1

                tree_a = apply_rewrite_safe(root_tree, a)
                root_a = decode(tree_a) if tree_a is not None else None

                tree_da_1 = apply_rewrite_safe(root_tree, b)
                tree_da_2 = apply_rewrite_safe(tree_da_1, a) if tree_da_1 is not None else None
                da_ok = tree_da_2 is not None
                root_da = decode(tree_da_2) if da_ok else None

                tree_ad_1 = apply_rewrite_safe(root_tree, a)
                tree_ad_2 = apply_rewrite_safe(tree_ad_1, b) if tree_ad_1 is not None else None
                ad_ok = tree_ad_2 is not None

                if da_ok:
                    da_valid += 1
                if not ad_ok:
                    ad_invalid += 1
                if da_ok and root_da == root_a:
                    absorbed += 1

                if len(samples) < args.sample_limit:
                    samples.append(
                        {
                            "root": root_g,
                            "a_target": a["target_path"],
                            "a_move": (a["old_child_g"], a["new_child_g"]),
                            "b_target": b["target_path"],
                            "b_move": (b["old_child_g"], b["new_child_g"]),
                            "ancestor_alone": root_a,
                            "desc_then_anc": root_da,
                            "da_valid": da_ok,
                            "ad_valid": ad_ok,
                            "absorbed": da_ok and root_da == root_a,
                        }
                    )

                bad = (
                    (not da_ok)
                    or ad_ok
                    or (root_a is None)
                    or (root_da != root_a)
                )
                if bad and len(mismatches) < 10:
                    mismatches.append(
                        {
                            "root": root_g,
                            "a_target": a["target_path"],
                            "a_move": (a["old_child_g"], a["new_child_g"]),
                            "b_target": b["target_path"],
                            "b_move": (b["old_child_g"], b["new_child_g"]),
                            "ancestor_alone": root_a,
                            "desc_then_anc": root_da,
                            "da_valid": da_ok,
                            "ad_valid": ad_ok,
                        }
                    )

    print(f"limit = {args.limit}")
    print(f"canonical_generators = {len(generators)}")
    print(f"sampled_prune_pairs = {sampled}")
    print(f"descendant_then_ancestor_valid = {da_valid}")
    print(f"ancestor_then_descendant_invalid = {ad_invalid}")
    print(f"absorbed_pairs = {absorbed}")
    print(f"mismatches = {len(mismatches)}")
    print()

    print("sample prune pairs:")
    for item in samples:
        print(
            f"root={item['root']} "
            f"A@{item['a_target']} {item['a_move'][0]}->{item['a_move'][1]} "
            f"B@{item['b_target']} {item['b_move'][0]}->{item['b_move'][1]} | "
            f"A_alone={item['ancestor_alone']} "
            f"B;A={item['desc_then_anc']} "
            f"DA_valid={item['da_valid']} AD_valid={item['ad_valid']} "
            f"absorbed={item['absorbed']}"
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
