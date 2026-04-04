#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pet.core import encode, decode, shape_generator
from tools.prune_absorption_check import (
    iter_subtree_paths,
    get_subtree_safe,
    set_subtree,
    replace_child_generator,
    child_generators,
    nearest_candidates,
)

def is_globally_canonical(tree):
    if tree is None:
        return True
    gs = child_generators(tree)
    if any(gs[i] < gs[i + 1] for i in range(len(gs) - 1)):
        return False
    for _, exp_repr in tree:
        if exp_repr is not None and not is_globally_canonical(exp_repr):
            return False
    return True

def is_locally_canonical(tree):
    gs = child_generators(tree)
    return all(gs[i] >= gs[i + 1] for i in range(len(gs) - 1))

def get_subtree(tree, path):
    cur = tree
    for idx in path:
        cur = cur[idx][1]
    return cur

def apply_rw(tree, path, child_idx, new_g):
    node = tree if path == () else get_subtree(tree, path)
    new_node = replace_child_generator(node, child_idx, new_g)
    return set_subtree(tree, path, new_node)

def all_paths_including_root(tree):
    yield ()
    yield from iter_subtree_paths(tree)

def main():
    parser = argparse.ArgumentParser(
        description="Root-inclusive one-step probe with local/global canonicity classification."
    )
    parser.add_argument("--limit", type=int, default=2000)
    parser.add_argument("--max-hits", type=int, default=20)
    args = parser.parse_args()

    pool = [1] + sorted({shape_generator(n) for n in range(2, args.limit + 1)})
    hits = []
    counts = {
        "globally_canonical": 0,
        "rewrite_node_ok_global_fail": 0,
        "other": 0,
    }

    for h in pool[1:]:
        tree0 = encode(h)

        for path in all_paths_including_root(tree0):
            node = tree0 if path == () else get_subtree(tree0, path)
            gs = child_generators(node)

            for child_idx in range(len(gs)):
                for new_g in nearest_candidates(gs, child_idx, pool):
                    if new_g <= gs[child_idx]:
                        continue

                    tree1 = apply_rw(tree0, path, child_idx, new_g)

                    local_node = tree1 if path == () else get_subtree(tree1, path)
                    local_ok = is_locally_canonical(local_node)
                    global_ok = is_globally_canonical(tree1)

                    item = {
                        "initial_h": h,
                        "new_h": decode(tree1),
                        "path": path,
                        "child_idx": child_idx,
                        "move": (gs[child_idx], new_g),
                        "root_child_gs_before": child_generators(tree0),
                        "root_child_gs_after": child_generators(tree1),
                        "after_child_gs": child_generators(local_node),
                        "local_ok": local_ok,
                        "global_ok": global_ok,
                    }

                    if local_ok and global_ok:
                        counts["globally_canonical"] += 1
                    elif local_ok and not global_ok:
                        counts["rewrite_node_ok_global_fail"] += 1
                    else:
                        counts["other"] += 1

                    if len(hits) < args.max_hits:
                        hits.append(item)
                if len(hits) >= args.max_hits and sum(counts.values()) >= args.max_hits:
                    break
            if len(hits) >= args.max_hits and sum(counts.values()) >= args.max_hits:
                break
        if len(hits) >= args.max_hits and sum(counts.values()) >= args.max_hits:
            break

    total = sum(counts.values())

    print(f"total_checked = {total}")
    print(f"globally_canonical = {counts['globally_canonical']}")
    print(f"rewrite_node_ok_global_fail = {counts['rewrite_node_ok_global_fail']}")
    print(f"other = {counts['other']}")
    print()
    print("sample hits:")
    for item in hits:
        print(
            f"initial_h={item['initial_h']} new_h={item['new_h']} "
            f"path={item['path']} child_idx={item['child_idx']} "
            f"move={item['move']} after_child_gs={item['after_child_gs']} "
            f"local_ok={item['local_ok']} global_ok={item['global_ok']}"
        )

    print()
    print("rewrite-node-ok/global-fail samples:")
    shown = 0
    for item in hits:
        if item["local_ok"] and not item["global_ok"]:
            print(
                f"initial_h={item['initial_h']} new_h={item['new_h']} "
                f"path={item['path']} child_idx={item['child_idx']} "
                f"move={item['move']} "
                f"root_before={item['root_child_gs_before']} "
                f"root_after={item['root_child_gs_after']} "
                f"after_child_gs={item['after_child_gs']}"
            )
            shown += 1
    if shown == 0:
        print("none in sample hits")

if __name__ == "__main__":
    raise SystemExit(main())
