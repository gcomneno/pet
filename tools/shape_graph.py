import json
from collections import Counter


def add_prime(shape):
    return tuple(sorted(shape + (("p", None),), key=str))


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


shape_list = list(shapes.keys())

print("total shapes:", len(shape_list))

edges = []

shape_set = set(shape_list)

for s in shape_list:
    child = add_prime(s)

    if child in shape_set:
        edges.append((s, child))


print("edges:", len(edges))

with open("pet_shape_graph.dot", "w") as f:

    f.write("digraph PET {\n")

    for s in shape_list:
        f.write(f'"{s}"\n')

    for a,b in edges:
        f.write(f'"{a}" -> "{b}"\n')

    f.write("}\n")
