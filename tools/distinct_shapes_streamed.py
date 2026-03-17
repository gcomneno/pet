import sys
import json

def normalize(node_list):
    shape = []

    for node in node_list:
        exp = node["e"]

        if exp is None:
            shape.append(("p", None))
        else:
            shape.append(("p", normalize(exp)))

    return tuple(sorted(shape, key=str))


shapes = set()

for line in sys.stdin:
    row = json.loads(line)

    shape = normalize(row["pet"])
    shapes.add(shape)

print("distinct shapes:", len(shapes))
