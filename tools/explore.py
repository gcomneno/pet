#!/usr/bin/env python3
"""Explore PET metrics across a range of integers."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pet import encode
from pet_metrics import extended_metrics


def explore(start: int, stop: int) -> None:
    print(f"{'N':>6}  {'nodes':>5}  {'leaves':>6}  {'height':>6}  {'maxbr':>5}  {'mass':>4}  {'vert':>6}  {'asym':>6}")
    print("-" * 62)
    for n in range(start, stop + 1):
        tree = encode(n)
        m = extended_metrics(tree)
        print(
            f"{n:>6}  "
            f"{m['node_count']:>5}  "
            f"{m['leaf_count']:>6}  "
            f"{m['height']:>6}  "
            f"{m['max_branching']:>5}  "
            f"{m['recursive_mass']:>4}  "
            f"{m['verticality_ratio']:>6.3f}  "
            f"{m['structural_asymmetry']:>6.3f}"
        )


if __name__ == "__main__":
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    stop  = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    explore(start, stop)
