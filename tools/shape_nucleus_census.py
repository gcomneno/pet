#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter, defaultdict, deque

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


def sort_shape(shape: Shape):
    return (node_count(shape), height(shape), max_branching(shape), render(shape))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("start", type=int)
    parser.add_argument("end", type=int)
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--top", type=int, default=15)
    parser.add_argument(
        "--exclude-generator",
        action="append",
        type=int,
        default=[1],
        help="Generator values to ignore in nucleus counts (default: 1)",
    )
    args = parser.parse_args()

    excluded = set(args.exclude_generator)

    nucleus_counter = Counter()
    nucleus_examples = defaultdict(list)

    first_counter = Counter()
    first_examples = defaultdict(list)

    origin_shapes = {}
    total_shapes = 0

    for n in range(args.start, args.end + 1):
        shape = shape_of_int(n)
        if shape in origin_shapes:
            continue
        origin_shapes[shape] = n
        total_shapes += 1

        reached = closure(shape, args.depth)

        # tutti i nuclei non esclusi raggiunti
        gens = sorted(
            {
                generator_of_shape(s)
                for s in reached
                if s != shape and generator_of_shape(s) not in excluded
            }
        )
        for g in gens:
            nucleus_counter[g] += 1
            if len(nucleus_examples[g]) < 8:
                nucleus_examples[g].append(n)

        # primo livello non banale raggiungibile
        candidate_depths = [
            d
            for s, d in reached.items()
            if s != shape and generator_of_shape(s) not in excluded
        ]
        if candidate_depths:
            best_depth = min(candidate_depths)
            first_gens = sorted(
                {
                    generator_of_shape(s)
                    for s, d in reached.items()
                    if s != shape and d == best_depth and generator_of_shape(s) not in excluded
                }
            )
            for g in first_gens:
                first_counter[g] += 1
                if len(first_examples[g]) < 8:
                    first_examples[g].append(n)

    print(f"range            = {args.start}..{args.end}")
    print(f"depth            = {args.depth}")
    print(f"excluded         = {sorted(excluded)}")
    print(f"unique_shapes    = {total_shapes}")
    print()

    print("top nuclei (excluding filtered generators)")
    for g, count in nucleus_counter.most_common(args.top):
        print(f"generator={g}\tcount={count}\texamples={first_examples[g] or nucleus_examples[g]}")

    print()
    print("first nontrivial nuclei")
    for g, count in first_counter.most_common(args.top):
        print(f"generator={g}\tcount={count}\texamples={first_examples[g]}")

    print()
    print("origin shape representatives")
    for shape, n in sorted(origin_shapes.items(), key=lambda item: sort_shape(item[0]))[:args.top]:
        print(f"n={n}\tgenerator={generator_of_shape(shape)}\trender={render(shape)}")


if __name__ == "__main__":
    main()
