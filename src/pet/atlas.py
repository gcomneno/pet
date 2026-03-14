import json


def extract_shape(node):
    if node is None:
        return None

    children = []

    for item in node:
        children.append(extract_shape(item["e"]))

    return tuple(children)


def shape_height(shape):
    if shape is None:
        return 1

    if not shape:
        return 1

    return 1 + max(shape_height(child) for child in shape)


def draw_shape(shape, prefix="", lines=None):
    if lines is None:
        lines = []

    lines.append(prefix + "•")

    for i, child in enumerate(shape):
        last = i == len(shape) - 1

        if last:
            branch = "└─"
            next_prefix = prefix + "  "
        else:
            branch = "├─"
            next_prefix = prefix + "│ "

        if child is None:
            lines.append(prefix + branch + "•")
        else:
            lines.append(prefix + branch + "•")
            draw_shape(child, next_prefix, lines)

    return lines


def omega_from_pet(node):
    total = 0

    for item in node:
        exp = item["e"]

        if exp is None:
            total += 1
        else:
            total += omega_from_pet(exp)

    return total


def atlas(path: str) -> dict:
    count = 0

    height_dist = {}
    shape_dist = {}
    shape_min_n = {}

    total_nodes = 0
    total_height = 0
    max_height = 0

    ratio_sum = 0

    shape_growth = []
    seen_shapes = set()

    omega_height_sum = {}
    omega_count = {}

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)

            n = rec["n"]
            m = rec["metrics"]

            h = m["height"]
            nodes = m["node_count"]

            count += 1
            total_nodes += nodes
            total_height += h

            if h > max_height:
                max_height = h

            height_dist[h] = height_dist.get(h, 0) + 1

            ratio_sum += nodes / h

            tree = rec["pet"]
            s = extract_shape(tree)

            shape_dist[s] = shape_dist.get(s, 0) + 1

            if s not in shape_min_n:
                shape_min_n[s] = n

            if s not in seen_shapes:
                seen_shapes.add(s)
                shape_growth.append((n, len(seen_shapes)))

            omega = omega_from_pet(tree)

            omega_height_sum[omega] = omega_height_sum.get(omega, 0) + h
            omega_count[omega] = omega_count.get(omega, 0) + 1

    shape_height_dist = {}
    shape_by_height = {}

    for s in shape_dist:
        h = shape_height(s)

        shape_height_dist[h] = shape_height_dist.get(h, 0) + 1
        shape_by_height[h] = shape_by_height.get(h, 0) + 1

    omega_avg_height = {}

    for k in omega_height_sum:
        omega_avg_height[k] = omega_height_sum[k] / omega_count[k]

    avg_ratio = ratio_sum / count

    return {
        "records": count,
        "height_dist": height_dist,
        "shape_dist": shape_dist,
        "shape_min_n": shape_min_n,
        "shape_height_dist": shape_height_dist,
        "shape_by_height": shape_by_height,
        "shape_growth": shape_growth,
        "omega_avg_height": omega_avg_height,
        "omega_count": omega_count,
        "avg_width_depth_ratio": avg_ratio,
        "max_height": max_height,
        "avg_nodes": total_nodes / count,
        "avg_height": total_height / count,
    }


def save_shapes(stats, path="pet_shapes.txt"):
    shapes = sorted(stats["shape_dist"].items(), key=lambda x: -x[1])

    with open(path, "w", encoding="utf-8") as f:
        f.write("PET Structural Shapes Atlas\n\n")

        for shape, count in shapes:

            n = stats["shape_min_n"][shape]

            f.write(f"count: {count}   smallest_n: {n}\n")

            lines = draw_shape(shape, lines=[])

            for line in lines:
                f.write(line + "\n")

            f.write("\n")


def print_atlas(stats: dict) -> None:
    print("PET Atlas")
    print()

    print(f"records: {stats['records']}")
    print()

    print("height distribution")
    for h in sorted(stats["height_dist"]):
        print(f" {h} : {stats['height_dist'][h]}")

    print()
    print(f"max height: {stats['max_height']}")
    print()

    print(f"average node_count: {stats['avg_nodes']:.3f}")
    print(f"average height: {stats['avg_height']:.3f}")

    print()
    print(f"average width/depth ratio: {stats['avg_width_depth_ratio']:.3f}")

    print()
    print("distinct structural shapes:", len(stats["shape_dist"]))

    print()
    print("shape depth histogram")

    for h in sorted(stats["shape_height_dist"]):
        print(f" height {h} : {stats['shape_height_dist'][h]}")

    print()
    print("structural shapes by height")

    for h in sorted(stats["shape_by_height"]):
        print(f" height {h} : {stats['shape_by_height'][h]} shapes")

    print()
    print("height vs Ω(n)")
    print()

    print("Ω(n)   count     avg_height")

    for k in sorted(stats["omega_avg_height"]):
        avg = stats["omega_avg_height"][k]
        count = stats["omega_count"][k]

        print(f"{k:<6} {count:<9} {avg:.3f}")

    print()
    print("shape discovery milestones")

    for n, count in stats["shape_growth"][:20]:
        print(f"N={n} → shapes={count}")

    print()
    print("top structural shapes")

    top = sorted(stats["shape_dist"].items(), key=lambda x: -x[1])[:10]

    for shape, count in top:
        print()
        print("count:", count, " smallest_n:", stats["shape_min_n"][shape])

        lines = draw_shape(shape, lines=[])

        for line in lines:
            print(line)

    save_shapes(stats)
