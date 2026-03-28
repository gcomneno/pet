#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess


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


def expr(n: int) -> str:
    if n == 1:
        return "1"
    child_generators = [e for _, e in factor(n)]
    return "<" + ",".join(expr(g) for g in child_generators) + ">"


def canonical_generator(n: int) -> int:
    out = subprocess.check_output(["pet", "generator", str(n)], text=True)
    return int(out.strip())


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print recursive generator expression for the canonical PET shape of N."
    )
    parser.add_argument("n", type=int, help="integer to inspect")
    args = parser.parse_args()

    if args.n < 2:
        raise SystemExit("n must be >= 2")

    g = canonical_generator(args.n)
    print(f"n = {args.n}")
    print(f"generator = {g}")
    print(f"expr = {expr(g)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
