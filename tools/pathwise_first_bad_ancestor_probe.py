#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pet.core import encode, decode, shape_generator
from tools.pathwise_one_step_probe import (
    get_subtree,
    apply_rw,
    is_locally_canonical,
    all_paths_including_root,
)
from tools.prune_absorption_check import child_generators, nearest_candidates


def all_ancestor_paths_inclusive(path):
    return [path[:i] for i in range(len(path) + 1)]


def first_bad_ancestor(tree, rewritten_path):
    for anc in reversed(all_ancestor_paths_inclusive(rewritten_path)):
        node = tree if anc == () else get_subtree(tree, anc)
        gs = child_generators(node)
        if any(gs[i] < gs[i + 1] for i in range(len(gs) - 1)):
            return anc, gs
    return None, None


def main():
    parser = argparse.ArgumentParser(
        description="Bounded one-step probe for first bad ancestor in local-ok/global-fail rewrites."
    )
    parser.add_argument("--limit", type=int, default=2000)
    parser.add_argument("--max-hits", type=int, default=10)
    args = parser.parse_args()

    pool = [1] + sorted({shape_generator(n) for n in range(2, args.limit + 1)})
    hits = []

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

                    if not local_ok:
                        continue

                    bad_path, bad_gs = first_bad_ancestor(tree1, path)
                    if bad_path is None:
                        continue

                    before_node = tree0 if bad_path == () else get_subtree(tree0, bad_path)
                    before_gs = child_generators(before_node)

                    hits.append(
                        {
                            "initial_h": h,
                            "new_h": decode(tree1),
                            "path": path,
                            "child_idx": child_idx,
                            "move": (gs[child_idx], new_g),
                            "first_bad_ancestor": bad_path,
                            "first_bad_before": before_gs,
                            "first_bad_after": bad_gs,
                            "failure_kind": "root" if bad_path == () else "embedded_ancestor",
                        }
                    )

                    if len(hits) >= args.max_hits:
                        break
                if len(hits) >= args.max_hits:
                    break
            if len(hits) >= args.max_hits:
                break
        if len(hits) >= args.max_hits:
            break

    print(f"hits = {len(hits)}")
    print("samples:")
    for item in hits:
        print(
            f"initial_h={item['initial_h']} new_h={item['new_h']} "
            f"path={item['path']} child_idx={item['child_idx']} move={item['move']} "
            f"first_bad_ancestor={item['first_bad_ancestor']} "
            f"first_bad_before={item['first_bad_before']} "
            f"first_bad_after={item['first_bad_after']} "
            f"failure_kind={item['failure_kind']}"
        )


if __name__ == "__main__":
    raise SystemExit(main())
