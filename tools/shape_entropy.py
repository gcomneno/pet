import json
import math
from collections import Counter


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

with open("./data/pet_1M.jsonl") as f:
    for line in f:
        row = json.loads(line)

        shape = normalize(row["pet"])
        shapes[shape] += 1


total = sum(shapes.values())

H = 0

for count in shapes.values():
    p = count / total
    H -= p * math.log(p)

print("shape entropy:", H)
print("max entropy:", math.log(len(shapes)))
