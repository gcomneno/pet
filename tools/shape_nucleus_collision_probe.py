#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
from collections import defaultdict
from pathlib import Path

from pet.core import encode


HERE = Path(__file__).resolve().parent
SIG_PATH = HERE / "shape_nucleus_signature.py"

spec = importlib.util.spec_from_file_location("shape_nucleus_signature", SIG_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


Shape = tuple


def canonical(shape: Shape) -> Shape:
    return tuple(sorted((canonical(child) for child in shape), key=repr))


def tree_to_shape(tree) -> Shape:
    children = []
    for _, exp_repr in tree:
        children.append(() if exp_repr is None else tree_to_shape(exp_repr))
    return canonical(tuple(children))


def shape_of_int(n: int) -> Shape:
    return tree_to_shape(encode(n))


def branch_profile(shape: Shape) -> list[int]:
    counts: list[int] = []

    def walk(s: Shape, depth: int) -> None:
        if depth == len(counts):
            counts.append(0)
        counts[depth] += len(s)
        for child in s:
            walk(child, depth + 1)

    walk(shape, 0)
    while counts and counts[-1] == 0:
        counts.pop()
    return counts


def metric_key(shape: Shape):
    return (
        mod.node_count(shape),
        mod.height(shape),
        mod.max_branching(shape),
        tuple(branch_profile(shape)),
    )


def nucleus_key(n: int, depth: int, excluded: set[int]):
    d = mod.signature_for_int(n, depth, excluded)
    return (
        tuple(d["first_nontrivial_nuclei"]),
        tuple(d["all_nontrivial_nuclei"]),
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("start", type=int)
    parser.add_argument("end", type=int)
    parser.add_argument("--depth", type=int, default=3)
    parser.add_argument("--top", type=int, default=20)
    parser.add_argument("--exclude-generator", action="append", type=int, default=[1])
    args = parser.parse_args()

    excluded = set(args.exclude_generator)

    rep_for_shape = {}
    for n in range(args.start, args.end + 1):
        s = shape_of_int(n)
        rep_for_shape.setdefault(s, n)

    groups = defaultdict(list)
    for shape, n in rep_for_shape.items():
        mk = metric_key(shape)
        nk = nucleus_key(n, args.depth, excluded)
        groups[mk].append((n, shape, nk))

    interesting = []
    for mk, items in groups.items():
        if len(items) < 2:
            continue
        nucleus_variants = {nk for _, _, nk in items}
        if len(nucleus_variants) > 1:
            interesting.append((mk, items))

    interesting.sort(key=lambda x: (-len(x[1]), x[0]))

    print(f"range = {args.start}..{args.end}")
    print(f"depth = {args.depth}")
    print(f"interesting_groups = {len(interesting)}")
    print()

    shown = 0
    for mk, items in interesting:
        shown += 1
        print(f"group {shown}")
        print(f"  metrics = node_count={mk[0]}, height={mk[1]}, max_branching={mk[2]}, branch_profile={list(mk[3])}")
        for n, shape, nk in sorted(items, key=lambda x: x[0]):
            print(f"  n={n:>4}  generator={mod.generator_of_shape(shape):>4}  render={mod.render(shape)}")
            print(f"         first={list(nk[0])}  all={list(nk[1])}")
        print()
        if shown >= args.top:
            break


if __name__ == "__main__":
    main()
