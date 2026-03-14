import json
import math
from collections import Counter

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

with open("./data/pet_1M.jsonl") as f:
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
