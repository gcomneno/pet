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


def choose_best_two_step_pathwise_move_toward_target(tree0, target, limit=2000):
    """Choose the best one- or two-step local-ok rewrite plan toward a numeric target."""
    first = choose_best_pathwise_move_toward_target(tree0, target=target, limit=limit)
    if first is None:
        return None

    best_plan = {
        "first_move": {
            "path": first["path"],
            "child_idx": first["child_idx"],
            "old_g": first["old_g"],
            "new_g": first["new_g"],
            "info": first["info"],
            "score": first["score"],
        },
        "steps": [first],
        "final_h": first["new_h"],
        "final_distance": abs(first["new_h"] - target),
    }

    second = choose_best_pathwise_move_toward_target(
        first["tree1"], target=target, limit=limit
    )

    if second is None:
        return best_plan

    second_distance = abs(second["new_h"] - target)
    if second_distance <= best_plan["final_distance"]:
        return {
            "first_move": {
                "path": first["path"],
                "child_idx": first["child_idx"],
                "old_g": first["old_g"],
                "new_g": first["new_g"],
                "info": first["info"],
                "score": first["score"],
            },
            "steps": [first, second],
            "final_h": second["new_h"],
            "final_distance": second_distance,
        }

    return best_plan


def lookahead_pathwise_build_toward_target(tree0, target, step_limit=5, limit=2000):
    """Build greedily toward a target using the first move of a two-step plan."""
    cur = tree0
    history = []
    stop_reason = "no_improving_move"

    for _ in range(step_limit):
        before_h = decode(cur)
        before_d = abs(before_h - target)

        plan = choose_best_two_step_pathwise_move_toward_target(
            cur, target=target, limit=limit
        )
        if plan is None:
            stop_reason = "no_candidate"
            break

        first = plan["steps"][0]
        after_h = decode(first["tree1"])
        after_d = abs(after_h - target)

        if after_d >= before_d:
            stop_reason = "no_improving_move"
            break

        history.append(
            {
                "path": first["path"],
                "child_idx": first["child_idx"],
                "old_g": first["old_g"],
                "new_g": first["new_g"],
                "score": first["score"],
                "info": first["info"],
                "distance_before": before_d,
                "distance_after": after_d,
                "new_h": after_h,
                "plan_final_h": plan["final_h"],
                "plan_final_distance": plan["final_distance"],
                "plan_step_count": len(plan["steps"]),
            }
        )

        cur = first["tree1"]
    else:
        stop_reason = "step_limit"

    return {
        "start_h": decode(tree0),
        "final_h": decode(cur),
        "target": target,
        "history": history,
        "stop_reason": stop_reason,
    }


def compare_builders_toward_target(tree0, target, step_limit=5, limit=2000):
    """Compare greedy and two-step lookahead builders on the same target."""
    greedy = greedy_pathwise_build_toward_target(
        tree0, target=target, step_limit=step_limit, limit=limit
    )
    lookahead = lookahead_pathwise_build_toward_target(
        tree0, target=target, step_limit=step_limit, limit=limit
    )

    return {
        "target": target,
        "greedy": {
            "start_h": greedy["start_h"],
            "final_h": greedy["final_h"],
            "final_distance": abs(greedy["final_h"] - target),
            "step_count": len(greedy["history"]),
            "stop_reason": greedy["stop_reason"],
        },
        "lookahead": {
            "start_h": lookahead["start_h"],
            "final_h": lookahead["final_h"],
            "final_distance": abs(lookahead["final_h"] - target),
            "step_count": len(lookahead["history"]),
            "stop_reason": lookahead["stop_reason"],
        },
    }


def summarize_build_result(result):
    """Return a compact summary for a builder result."""
    steps = []
    for step in result["history"]:
        steps.append(
            {
                "path": step["path"],
                "child_idx": step["child_idx"],
                "old_g": step["old_g"],
                "new_g": step["new_g"],
                "new_h": step["new_h"],
                "distance_before": step["distance_before"],
                "distance_after": step["distance_after"],
            }
        )

    return {
        "start_h": result["start_h"],
        "target": result["target"],
        "final_h": result["final_h"],
        "initial_distance": abs(result["start_h"] - result["target"]),
        "final_distance": abs(result["final_h"] - result["target"]),
        "step_count": len(result["history"]),
        "stop_reason": result["stop_reason"],
        "steps": steps,
    }


def choose_best_seed_toward_target(
    target, seed_ns, builder="lookahead", step_limit=5, limit=2000, policy="balanced"
):
    """Run a builder from multiple seeds and return the best result."""
    candidates = []

    normalized_seed_entries = [
        item if isinstance(item, dict) else {"seed": item}
        for item in seed_ns
    ]

    for entry in normalized_seed_entries:
        seed_n = entry["seed"]
        tree0 = encode(seed_n)

        if builder == "greedy":
            result = greedy_pathwise_build_toward_target(
                tree0, target=target, step_limit=step_limit, limit=limit
            )
        elif builder == "lookahead":
            result = lookahead_pathwise_build_toward_target(
                tree0, target=target, step_limit=step_limit, limit=limit
            )
        else:
            raise ValueError("builder must be 'greedy' or 'lookahead'")

        summary = summarize_build_result(result)
        summary["seed_n"] = seed_n
        summary["seed_source"] = entry.get("source")
        summary["seed_source_rank"] = entry.get("source_rank")
        summary["seed_distance_to_target"] = entry.get("distance_to_target")
        summary["seed_priority_key"] = entry.get("priority_key")
        candidates.append(summary)

    def chooser_policy_rank(item):
        source = item.get("seed_source")
        if policy == "scale_first":
            rank_map = {
                "scale_anchor": 0,
                "below": 1,
                "above": 2,
                "fill": 3,
                None: 999,
            }
        else:
            rank_map = {
                "below": 0,
                "above": 1,
                "scale_anchor": 2,
                "fill": 3,
                None: 999,
            }
        return rank_map.get(source, 999)

    candidates.sort(
        key=lambda item: (
            item["final_distance"],
            chooser_policy_rank(item),
            item.get("seed_distance_to_target", 999999999),
            -item.get("step_count", 0),
            item["seed_n"],
        )
    )
    best = candidates[0]
    best_seed_entry = next(
        entry for entry in normalized_seed_entries
        if entry["seed"] == best["seed_n"]
    )

    selection_summary = {
        "best_seed": best["seed_n"],
        "best_seed_source": best_seed_entry.get("source"),
        "best_seed_priority_key": best_seed_entry.get("priority_key"),
        "initial_distance": best["initial_distance"],
        "final_distance": best["final_distance"],
        "improvement": best["initial_distance"] - best["final_distance"],
    }

    return {
        "target": target,
        "policy": policy,
        "builder": builder,
        "best_seed": best["seed_n"],
        "best_seed_entry": best_seed_entry,
        "best_result": best,
        "candidates": candidates,
        "selection_summary": selection_summary,
    }

def propose_seed_family_for_target(target, pool_limit=2000, top_k=12, policy="balanced"):
    """Return a small bounded top-down seed family around the target.

    Policies:
    - balanced: below -> above -> scale_anchor -> fill
    - scale_first: below -> above -> scale_anchor -> fill, but with scale anchors
      ranked ahead of fill candidates in priority metadata
    """
    if policy not in {"balanced", "scale_first"}:
        raise ValueError("policy must be 'balanced' or 'scale_first'")

    pool = sorted({shape_generator(n) for n in range(2, pool_limit + 1)})
    ranked = sorted(pool, key=lambda n: (abs(n - target), n))
    below = [n for n in ranked if n < target]
    above = [n for n in ranked if n > target]

    side_quota = min(2, top_k // 2)
    reserved_below = below[:side_quota]
    reserved_above = above[:side_quota]
    reserved = set(reserved_below) | set(reserved_above)

    if policy == "scale_first":
        lower_scale = max(2, target // 4)
        upper_scale = min(pool_limit, target * 2)
    else:
        lower_scale = max(2, target // 2)
        upper_scale = min(pool_limit, target * 2)
    scale_anchor = [
        n for n in ranked
        if lower_scale <= n <= upper_scale and n not in reserved
    ]

    if policy == "balanced":
        source_rank_map = {
            "below": 0,
            "above": 1,
            "scale_anchor": 2,
            "fill": 3,
        }
    else:
        source_rank_map = {
            "below": 0,
            "scale_anchor": 1,
            "above": 2,
            "fill": 3,
        }

    out = []
    seen = set()
    insertion_index = 0

    scale_quota = 1 if policy == "balanced" else 2

    for source, bucket in (
        ("below", reserved_below),
        ("above", reserved_above),
        ("scale_anchor", scale_anchor[:scale_quota]),
        ("fill", ranked),
    ):
        for n in bucket:
            if n in seen:
                continue
            seen.add(n)
            out.append(
                {
                    "seed": n,
                    "source": source,
                    "source_rank": source_rank_map[source],
                    "distance_to_target": abs(n - target),
                    "priority_key": (
                        source_rank_map[source],
                        abs(n - target),
                        n,
                        insertion_index,
                    ),
                }
            )
            insertion_index += 1
            if len(out) >= top_k:
                return sorted(out, key=lambda item: item["priority_key"])

    return sorted(out, key=lambda item: item["priority_key"])

def auto_build_toward_target(
    target,
    pool_limit=2000,
    top_k=12,
    builder="lookahead",
    step_limit=5,
    limit=2000,
    policy="balanced",
):
    """Run the full bounded bottom-up pipeline toward a target."""
    seed_family = propose_seed_family_for_target(
        target=target,
        pool_limit=pool_limit,
        top_k=top_k,
        policy=policy,
    )

    selection = choose_best_seed_toward_target(
        target=target,
        seed_ns=seed_family,
        builder=builder,
        step_limit=step_limit,
        limit=limit,
        policy=policy,
    )

    seed_entry_by_n = {item["seed"]: item for item in seed_family}
    enriched_candidates = [
        {
            **item,
            "seed_source": seed_entry_by_n[item["seed_n"]]["source"],
            "seed_source_rank": seed_entry_by_n[item["seed_n"]]["source_rank"],
            "seed_distance_to_target": seed_entry_by_n[item["seed_n"]]["distance_to_target"],
            "seed_priority_key": seed_entry_by_n[item["seed_n"]]["priority_key"],
        }
        for item in selection["candidates"]
    ]

    best_seed_entry = next(
        item for item in seed_family if item["seed"] == selection["best_seed"]
    )

    enriched_best_result = {
        **selection["best_result"],
        "seed_source": best_seed_entry["source"],
        "seed_source_rank": best_seed_entry["source_rank"],
        "seed_distance_to_target": best_seed_entry["distance_to_target"],
        "seed_priority_key": best_seed_entry["priority_key"],
    }

    selection_summary = {
        "best_seed": enriched_best_result["seed_n"],
        "best_seed_source": enriched_best_result["seed_source"],
        "best_seed_priority_key": enriched_best_result["seed_priority_key"],
        "initial_distance": enriched_best_result["initial_distance"],
        "final_distance": enriched_best_result["final_distance"],
        "improvement": (
            enriched_best_result["initial_distance"]
            - enriched_best_result["final_distance"]
        ),
    }

    def auto_build_policy_rank(item):
        source = item.get("seed_source")
        if policy == "scale_first":
            rank_map = {
                "scale_anchor": 0,
                "below": 1,
                "above": 2,
                "fill": 3,
                None: 999,
            }
        else:
            rank_map = {
                "below": 0,
                "above": 1,
                "scale_anchor": 2,
                "fill": 3,
                None: 999,
            }
        return rank_map.get(source, 999)

    enriched_candidates = sorted(
        enriched_candidates,
        key=lambda item: (
            item["final_distance"],
            auto_build_policy_rank(item),
            item.get("seed_distance_to_target", 999999999),
            -item.get("step_count", 0),
            item["seed_n"],
        ),
    )

    best_candidate = enriched_candidates[0]

    return {
        "target": target,
        "policy": policy,
        "builder": builder,
        "seed_family": seed_family,
        "best_seed": best_candidate["seed_n"],
        "best_seed_entry": next(item for item in seed_family if item["seed"] == best_candidate["seed_n"]),
        "best_result": {
            **enriched_best_result,
            "seed_n": best_candidate["seed_n"],
            "seed_source": best_candidate["seed_source"],
            "seed_source_rank": best_candidate["seed_source_rank"],
            "seed_distance_to_target": best_candidate["seed_distance_to_target"],
            "seed_priority_key": best_candidate["seed_priority_key"],
            "final_distance": best_candidate["final_distance"],
        },
        "candidates": enriched_candidates,
        "selection_summary": selection_summary,
    }


def plateau_tolerant_lookahead_build_toward_target(
    tree0, target, step_limit=5, limit=2000
):
    """Build toward a target using two-step plans, allowing neutral first steps
    only when the full two-step plan improves the final distance.
    """
    cur = tree0
    history = []
    stop_reason = "no_improving_plan"

    for _ in range(step_limit):
        before_h = decode(cur)
        before_d = abs(before_h - target)

        plan = choose_best_two_step_pathwise_move_toward_target(
            cur, target=target, limit=limit
        )
        if plan is None:
            stop_reason = "no_candidate"
            break

        first = plan["steps"][0]
        first_h = decode(first["tree1"])
        first_d = abs(first_h - target)
        plan_final_d = plan["final_distance"]

        if plan_final_d >= before_d:
            stop_reason = "no_improving_plan"
            break

        history.append(
            {
                "path": first["path"],
                "child_idx": first["child_idx"],
                "old_g": first["old_g"],
                "new_g": first["new_g"],
                "score": first["score"],
                "info": first["info"],
                "distance_before": before_d,
                "distance_after": first_d,
                "new_h": first_h,
                "plan_final_h": plan["final_h"],
                "plan_final_distance": plan_final_d,
                "plan_step_count": len(plan["steps"]),
            }
        )

        cur = first["tree1"]
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
