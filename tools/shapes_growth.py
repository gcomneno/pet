import json


def extract_shape(node):
    if node is None:
        return None

    children = []

    for item in node:
        children.append(extract_shape(item["e"]))

    return tuple(children)


def shapes_growth(path, step=1000):
    seen = set()
    result = []

    next_checkpoint = step

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)

            n = rec["n"]
            tree = rec["pet"]

            shape = extract_shape(tree)
            seen.add(shape)

            if n >= next_checkpoint:
                result.append((n, len(seen)))
                next_checkpoint += step

    return result


def print_growth(data):
    print("PET shape growth")
    print()
    print("N       shapes")

    for n, s in data:
        print(f"{n:<8} {s}")


def save_growth(data, path="pet_shapes_growth.txt"):
    with open(path, "w", encoding="utf-8") as f:
        f.write("N shapes\n")

        for n, s in data:
            f.write(f"{n} {s}\n")
