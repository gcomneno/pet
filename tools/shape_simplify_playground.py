#!/usr/bin/env python3
from __future__ import annotations

import argparse

from pet.core import encode


Shape = tuple


def canonical(shape):
    return tuple(sorted((canonical(child) for child in shape), key=repr))


def tree_to_shape(tree) -> Shape:
    children = []
    for _, exp_repr in tree:
        children.append(() if exp_repr is None else tree_to_shape(exp_repr))
    return canonical(tuple(children))


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


def render(shape: Shape) -> str:
    if not shape:
        return "[]"
    return "[" + ", ".join(render(child) for child in shape) + "]"


def prune_leaf_once(shape: Shape):
    # depth-first: prima prova sotto
    for i, child in enumerate(shape):
        new_child, changed = prune_leaf_once(child)
        if changed:
            items = list(shape)
            items[i] = new_child
            return canonical(tuple(items)), True

    # poi localmente: rimuovi una foglia se c'è
    if () in shape:
        items = list(shape)
        items.remove(())
        return canonical(tuple(items)), True

    return shape, False


def contract_unary_once(shape: Shape):
    # localmente: collassa una catena unaria non-banale
    if len(shape) == 1 and shape[0] != ():
        return canonical(shape[0]), True

    # altrimenti prova sotto
    for i, child in enumerate(shape):
        new_child, changed = contract_unary_once(child)
        if changed:
            items = list(shape)
            items[i] = new_child
            return canonical(tuple(items)), True

    return shape, False


def dedup_siblings_once(shape: Shape):
    unique = []
    seen = set()
    for child in shape:
        if child not in seen:
            unique.append(child)
            seen.add(child)

    if len(unique) < len(shape):
        return canonical(tuple(unique)), True

    for i, child in enumerate(shape):
        new_child, changed = dedup_siblings_once(child)
        if changed:
            items = list(shape)
            items[i] = new_child
            return canonical(tuple(items)), True

    return shape, False


OPS = {
    "prune-leaf": prune_leaf_once,
    "contract-unary": contract_unary_once,
    "dedup-siblings": dedup_siblings_once,
}


def shape_of_int(n: int) -> Shape:
    return tree_to_shape(encode(n))


def print_shape(label: str, shape: Shape) -> None:
    print(label)
    print("  render        =", render(shape))
    print("  node_count    =", node_count(shape))
    print("  height        =", height(shape))
    print("  max_branching =", max_branching(shape))


def cmd_show(args):
    for n in args.n:
        shape = shape_of_int(n)
        print(f"N = {n}")
        print_shape("shape", shape)
        print()


def cmd_compare(args):
    a = shape_of_int(args.n1)
    b = shape_of_int(args.n2)
    print(f"N1 = {args.n1}")
    print_shape("shape1", a)
    print()
    print(f"N2 = {args.n2}")
    print_shape("shape2", b)
    print()
    print("same_shape =", a == b)


def cmd_simplify(args):
    shape = shape_of_int(args.n)
    op = OPS[args.op]

    print(f"N = {args.n}")
    print_shape("original", shape)
    print()

    current = shape
    for step in range(1, args.steps + 1):
        new_shape, changed = op(current)
        if not changed:
            print(f"step {step}: no-op")
            break

        print_shape(f"step {step}", new_shape)
        print()
        current = new_shape


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_show = sub.add_parser("show")
    p_show.add_argument("n", nargs="+", type=int)
    p_show.set_defaults(func=cmd_show)

    p_compare = sub.add_parser("compare")
    p_compare.add_argument("n1", type=int)
    p_compare.add_argument("n2", type=int)
    p_compare.set_defaults(func=cmd_compare)

    p_simplify = sub.add_parser("simplify")
    p_simplify.add_argument("op", choices=sorted(OPS))
    p_simplify.add_argument("n", type=int)
    p_simplify.add_argument("--steps", type=int, default=3)
    p_simplify.set_defaults(func=cmd_simplify)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
