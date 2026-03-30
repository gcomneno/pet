#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import deque

from pet.core import decode, encode


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


def render(shape: Shape) -> str:
    if not shape:
        return "[]"
    return "[" + ", ".join(render(child) for child in shape) + "]"


def node_count(shape: Shape) -> int:
    return sum(1 + node_count(child) for child in shape)


def height(shape: Shape) -> int:
    if not shape:
        return 0
    return max(1 + height(child) for child in shape)


def max_branching(shape: Shape) -> int:
    here = len(shape)
    below = [max_branching(child) for child in shape]
    return max([here] + below) if below else here


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def first_primes(count: int) -> list[int]:
    out = []
    x = 2
    while len(out) < count:
        if is_prime(x):
            out.append(x)
        x += 1 if x == 2 else 2
    return out


def shape_to_minimal_tree(shape: Shape):
    primes = first_primes(len(shape))
    out = []
    for p, child in zip(primes, shape):
        out.append((p, None if child == () else shape_to_minimal_tree(child)))
    return out


def generator_of_shape(shape: Shape) -> int:
    if shape == ():
        return 1
    return decode(shape_to_minimal_tree(shape))


def prune_leaf_variants(shape: Shape) -> set[Shape]:
    out: set[Shape] = set()

    for i, child in enumerate(shape):
        if child == ():
            items = list(shape)
            del items[i]
            out.add(canonical(tuple(items)))

    for i, child in enumerate(shape):
        for sub in prune_leaf_variants(child):
            items = list(shape)
            items[i] = sub
            out.add(canonical(tuple(items)))

    return out


def contract_unary_variants(shape: Shape) -> set[Shape]:
    out: set[Shape] = set()

    if len(shape) == 1 and shape[0] != ():
        out.add(canonical(shape[0]))

    for i, child in enumerate(shape):
        for sub in contract_unary_variants(child):
            items = list(shape)
            items[i] = sub
            out.add(canonical(tuple(items)))

    return out


def dedup_siblings_variants(shape: Shape) -> set[Shape]:
    out: set[Shape] = set()

    unique = []
    seen = set()
    for child in shape:
        if child not in seen:
            unique.append(child)
            seen.add(child)

    if len(unique) < len(shape):
        out.add(canonical(tuple(unique)))

    for i, child in enumerate(shape):
        for sub in dedup_siblings_variants(child):
            items = list(shape)
            items[i] = sub
            out.add(canonical(tuple(items)))

    return out


OPS = {
    "prune-leaf": prune_leaf_variants,
    "contract-unary": contract_unary_variants,
    "dedup-siblings": dedup_siblings_variants,
}


def one_step_neighbors(shape: Shape) -> dict[Shape, set[str]]:
    by_shape: dict[Shape, set[str]] = {}
    for op_name, fn in OPS.items():
        for variant in fn(shape):
            if variant == shape:
                continue
            by_shape.setdefault(variant, set()).add(op_name)
    return by_shape


def closure(shape: Shape, depth: int) -> dict[Shape, int]:
    seen = {shape: 0}
    q = deque([(shape, 0)])

    while q:
        cur, d = q.popleft()
        if d >= depth:
            continue
        for nxt in one_step_neighbors(cur):
            if nxt not in seen:
                seen[nxt] = d + 1
                q.append((nxt, d + 1))

    return seen


def signature_for_int(n: int, depth: int, excluded: set[int]) -> dict:
    shape = shape_of_int(n)
    reached = closure(shape, depth)

    all_nuclei = sorted(
        {
            generator_of_shape(s)
            for s in reached
            if s != shape and generator_of_shape(s) not in excluded
        }
    )

    candidate_depths = [
        d for s, d in reached.items()
        if s != shape and generator_of_shape(s) not in excluded
    ]
    if candidate_depths:
        best_depth = min(candidate_depths)
        first_nuclei = sorted(
            {
                generator_of_shape(s)
                for s, d in reached.items()
                if s != shape and d == best_depth and generator_of_shape(s) not in excluded
            }
        )
    else:
        first_nuclei = []

    return {
        "n": n,
        "generator": generator_of_shape(shape),
        "render": render(shape),
        "node_count": node_count(shape),
        "height": height(shape),
        "max_branching": max_branching(shape),
        "first_nontrivial_nuclei": first_nuclei,
        "all_nontrivial_nuclei": all_nuclei,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("n", nargs="+", type=int)
    parser.add_argument("--depth", type=int, default=3)
    parser.add_argument("--exclude-generator", action="append", type=int, default=[1])
    args = parser.parse_args()

    excluded = set(args.exclude_generator)

    for n in args.n:
        d = signature_for_int(n, args.depth, excluded)
        print(f"N = {d['n']}")
        print("  generator              =", d["generator"])
        print("  render                 =", d["render"])
        print("  node_count             =", d["node_count"])
        print("  height                 =", d["height"])
        print("  max_branching          =", d["max_branching"])
        print("  first_nontrivial       =", d["first_nontrivial_nuclei"])
        print("  all_nontrivial         =", d["all_nontrivial_nuclei"])
        print()


if __name__ == "__main__":
    main()
