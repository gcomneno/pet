import json
import math
import sys
from pathlib import Path
from collections import Counter

INPUT_FILE = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("docs/reports/data/scan-2-1000000.jsonl")

CHECKPOINTS = [
    10_000,
    100_000,
    1_000_000
]

def normalize(node_list):
    shape = []

    for node in node_list:
        exp = node["e"]

        if exp is None:
            shape.append(("p", None))
        else:
            shape.append(("p", normalize(exp)))

    return tuple(sorted(shape, key=str))


shapes = Counter()

results = {}

current_n = 0

with INPUT_FILE.open(encoding="utf-8") as f:
    for line in f:
        row = json.loads(line)

        n = row["n"]

        shape = normalize(row["pet"])
        shapes[shape] += 1

        current_n = n

        if n in CHECKPOINTS:
            total = sum(shapes.values())

            H = 0
            for c in shapes.values():
                p = c / total
                H -= p * math.log(p)

            results[n] = H


print("N        entropy      loglog(N)")
print("--------------------------------")

for n in CHECKPOINTS:
    print(
        f"{n:<8d} {results[n]:.4f}      {math.log(math.log(n)):.4f}"
    )
