#!/usr/bin/env python3
from __future__ import annotations

import argparse

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


def sort_key(shape: Shape):
    return (node_count(shape), height(shape), max_branching(shape), render(shape))


def cmd_neighbors(args):
    shape = shape_of_int(args.n)

    by_shape: dict[Shape, set[str]] = {}
    for op_name, fn in OPS.items():
        for variant in fn(shape):
            if variant == shape:
                continue
            by_shape.setdefault(variant, set()).add(op_name)

    print(f"N = {args.n}")
    print("original")
    print("  render        =", render(shape))
    print("  generator     =", generator_of_shape(shape))
    print("  node_count    =", node_count(shape))
    print("  height        =", height(shape))
    print("  max_branching =", max_branching(shape))
    print()

    if not by_shape:
        print("no one-step simplifications")
        return

    for i, variant in enumerate(sorted(by_shape, key=sort_key), 1):
        ops = ", ".join(sorted(by_shape[variant]))
        print(f"neighbor {i}")
        print("  via           =", ops)
        print("  render        =", render(variant))
        print("  generator     =", generator_of_shape(variant))
        print("  node_count    =", node_count(variant))
        print("  height        =", height(variant))
        print("  max_branching =", max_branching(variant))
        print()


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("neighbors")
    p.add_argument("n", type=int)
    p.set_defaults(func=cmd_neighbors)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
