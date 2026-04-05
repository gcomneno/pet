"""Utilities for classifying pathwise rewrite failures."""

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pet.core import decode, encode, shape_generator
from tools.pathwise_one_step_probe import (
    get_subtree,
    apply_rw,
    is_locally_canonical,
    all_paths_including_root,
)
from tools.prune_absorption_check import child_generators, nearest_candidates


def all_ancestor_paths_inclusive(path):
    """Return all ancestor paths from root to the given path."""
    return [path[:i] for i in range(len(path) + 1)]


def first_bad_ancestor(tree, rewritten_path):
    """Return the first ancestor on the rewritten path that becomes non-canonical."""
    for anc in reversed(all_ancestor_paths_inclusive(rewritten_path)):
        node = tree if anc == () else get_subtree(tree, anc)
        gs = child_generators(node)
        if any(gs[i] < gs[i + 1] for i in range(len(gs) - 1)):
            return anc, gs
    return None, None


def pathwise_ceiling_trace(tree0, tree1, rewritten_path):
    """Return before/after local canonicity data along the rewritten path."""
    trace = []

    for anc in all_ancestor_paths_inclusive(rewritten_path):
        node0 = tree0 if anc == () else get_subtree(tree0, anc)
        node1 = tree1 if anc == () else get_subtree(tree1, anc)

        trace.append(
            {
                "path": anc,
                "before": child_generators(node0),
                "after": child_generators(node1),
                "locally_canonical": is_locally_canonical(node1),
            }
        )

    return trace


def first_bad_path_from_trace(trace):
    """Return the first non-canonical path found in a pathwise trace."""
    for item in trace:
        if not item["locally_canonical"]:
            return item["path"]
    return None


def first_violation_from_trace(trace):
    """Return the first local ceiling inversion found in a pathwise trace."""
    for item in trace:
        gs = item["after"]
        for i in range(len(gs) - 1):
            if gs[i] < gs[i + 1]:
                return {
                    "path": item["path"],
                    "index": i,
                    "left": gs[i],
                    "right": gs[i + 1],
                }
    return None


def local_ceiling_violations(gs):
    """Return all local ceiling inversions in a generator list."""
    out = []
    for i in range(len(gs) - 1):
        if gs[i] < gs[i + 1]:
            out.append(
                {
                    "index": i,
                    "left": gs[i],
                    "right": gs[i + 1],
                }
            )
    return out


def classify_pathwise_rewrite(tree0, tree1, rewritten_path):
    """Classify a rewritten path by local/global failure location."""
    local1 = tree1 if rewritten_path == () else get_subtree(tree1, rewritten_path)
    trace = pathwise_ceiling_trace(tree0, tree1, rewritten_path)
    first_bad_path = first_bad_path_from_trace(trace)
    first_violation = first_violation_from_trace(trace)

    if first_bad_path is None:
        failure_kind = None
    elif first_bad_path == ():
        failure_kind = "root"
    else:
        failure_kind = "embedded_ancestor"

    return {
        "local_ok": is_locally_canonical(local1),
        "trace": trace,
        "first_bad_path": first_bad_path,
        "first_violation": first_violation,
        "failure_kind": failure_kind,
    }



def root_failure_signature(tree0, tree1, rewritten_path):
    """Return a compact diagnostic signature for a root failure case."""
    info = classify_pathwise_rewrite(tree0, tree1, rewritten_path)

    if info["first_bad_path"] is None:
        bad_after = []
    else:
        bad_after = next(
            item["after"] for item in info["trace"] if item["path"] == info["first_bad_path"]
        )

    return {
        "local_ok": info["local_ok"],
        "first_bad_path": info["first_bad_path"],
        "violation_count_at_bad_path": len(local_ceiling_violations(bad_after)),
        "first_violation": info["first_violation"],
    }


def score_pathwise_move(tree0, tree1, rewritten_path, info=None):
    """Return a lexicographic score for comparing one-step pathwise rewrites.

    Higher is better. Priority order:
    1. no failure > embedded_ancestor > root
    2. smaller first violation is better
    3. larger numeric growth is better
    """

    if info is None:
        info = classify_pathwise_rewrite(tree0, tree1, rewritten_path)

    if info["failure_kind"] is None:
        tier = 3
    elif info["failure_kind"] == "embedded_ancestor":
        tier = 2
    else:
        tier = 1

    violation_penalty = 0
    if info["first_violation"] is not None:
        violation_penalty = (
            info["first_violation"]["right"] - info["first_violation"]["left"]
        )

    growth = decode(tree1) - decode(tree0)

    return (tier, -violation_penalty, growth)


def choose_best_pathwise_move(tree0, limit=2000):
    """Choose the best local-ok one-step rewrite under the current pathwise score."""
    pool = [1] + sorted({shape_generator(n) for n in range(2, limit + 1)})

    best = None
    best_score = None

    for path in all_paths_including_root(tree0):
        node = tree0 if path == () else get_subtree(tree0, path)
        gs = child_generators(node)

        for child_idx, old_g in enumerate(gs):
            for new_g in nearest_candidates(gs, child_idx, pool):
                if new_g <= old_g:
                    continue

                tree1 = apply_rw(tree0, path, child_idx, new_g)
                local1 = tree1 if path == () else get_subtree(tree1, path)

                if not is_locally_canonical(local1):
                    continue

                info = classify_pathwise_rewrite(tree0, tree1, path)
                score = score_pathwise_move(tree0, tree1, path, info)

                if best_score is None or score > best_score:
                    best_score = score
                    best = {
                        "path": path,
                        "child_idx": child_idx,
                        "old_g": old_g,
                        "new_g": new_g,
                        "tree1": tree1,
                        "info": info,
                        "score": score,
                    }

    return best


def choose_best_pathwise_move_toward_target(tree0, target, limit=2000):
    """Choose the best local-ok one-step rewrite toward a numeric target."""
    pool = [1] + sorted({shape_generator(n) for n in range(2, limit + 1)})

    best = None
    best_key = None

    for path in all_paths_including_root(tree0):
        node = tree0 if path == () else get_subtree(tree0, path)
        gs = child_generators(node)

        for child_idx, old_g in enumerate(gs):
            for new_g in nearest_candidates(gs, child_idx, pool):
                if new_g <= old_g:
                    continue

                tree1 = apply_rw(tree0, path, child_idx, new_g)
                local1 = tree1 if path == () else get_subtree(tree1, path)
                if not is_locally_canonical(local1):
                    continue

                info = classify_pathwise_rewrite(tree0, tree1, path)
                new_h = decode(tree1)

                if info["failure_kind"] is None:
                    tier = 3
                elif info["failure_kind"] == "embedded_ancestor":
                    tier = 2
                else:
                    tier = 1

                violation_penalty = 0
                if info["first_violation"] is not None:
                    violation_penalty = (
                        info["first_violation"]["right"] - info["first_violation"]["left"]
                    )

                key = (
                    -abs(new_h - target),
                    tier,
                    -violation_penalty,
                )

                if best_key is None or key > best_key:
                    best_key = key
                    best = {
                        "path": path,
                        "child_idx": child_idx,
                        "old_g": old_g,
                        "new_g": new_g,
                        "tree1": tree1,
                        "new_h": new_h,
                        "info": info,
                        "score": key,
                    }

    return best


def greedy_pathwise_build_toward_target(tree0, target, step_limit=5, limit=2000):
    """Greedily apply target-aware one-step rewrites while distance improves."""
    cur = tree0
    history = []
    stop_reason = "no_improving_move"

    for _ in range(step_limit):
        before_h = decode(cur)
        before_d = abs(before_h - target)

        best = choose_best_pathwise_move_toward_target(cur, target=target, limit=limit)
        if best is None:
            stop_reason = "no_candidate"
            break

        after_h = best["new_h"]
        after_d = abs(after_h - target)

        if after_d >= before_d:
            stop_reason = "no_improving_move"
            break

        history.append(
            {
                "path": best["path"],
                "child_idx": best["child_idx"],
                "old_g": best["old_g"],
                "new_g": best["new_g"],
                "score": best["score"],
                "info": best["info"],
                "distance_before": before_d,
                "distance_after": after_d,
                "new_h": after_h,
            }
        )

        cur = best["tree1"]
    else:
        stop_reason = "step_limit"

    return {
        "start_h": decode(tree0),
        "final_h": decode(cur),
        "target": target,
        "history": history,
        "stop_reason": stop_reason,
    }


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
