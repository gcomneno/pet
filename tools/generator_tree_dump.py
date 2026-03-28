#!/usr/bin/env python3
from __future__ import annotations

import argparse


def factor(n: int) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    d = 2
    while d * d <= n:
        e = 0
        while n % d == 0:
            n //= d
            e += 1
        if e:
            out.append((d, e))
        d = 3 if d == 2 else d + 2
    if n > 1:
        out.append((n, 1))
    return out


def primes(count: int) -> list[int]:
    out: list[int] = []
    candidate = 2
    while len(out) < count:
        ok = True
        for p in out:
            if p * p > candidate:
                break
            if candidate % p == 0:
                ok = False
                break
        if ok:
            out.append(candidate)
        candidate += 1 if candidate == 2 else 2
    return out


def primorial(k: int) -> int:
    out = 1
    for p in primes(k):
        out *= p
    return out


def dump_generator_tree(n: int, indent: int = 0) -> None:
    pad = "  " * indent
    fs = factor(n)
    child_generators = [e for _, e in fs]
    k = len(child_generators)
    base = primorial(k)
    ratio = n // base

    print(
        f"{pad}generator={n} "
        f"arity={k} "
        f"primorial={base} "
        f"local_ratio={ratio} "
        f"child_generators={child_generators}"
    )

    for g in child_generators:
        if g > 1:
            dump_generator_tree(g, indent + 1)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Dump the recursive generator tree of a canonical PET generator."
    )
    parser.add_argument("n", type=int, help="integer to inspect")
    args = parser.parse_args()

    if args.n < 2:
        raise SystemExit("n must be >= 2")

    dump_generator_tree(args.n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
