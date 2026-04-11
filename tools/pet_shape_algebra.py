from __future__ import annotations

from functools import lru_cache
from typing import TypeAlias

Shape: TypeAlias = tuple["Shape", ...]
PathT: TypeAlias = tuple[int, ...]
StableStepT: TypeAlias = tuple["Shape", int]
StablePathT: TypeAlias = tuple[StableStepT, ...]
PartialShape = "Shape | None | tuple[PartialShape, ...]"

PRIMITIVE_ROOT_OPS: tuple[str, ...] = ("NEW", "DROP")
PRIMITIVE_LOCAL_OPS: tuple[str, ...] = ("INC", "DEC")
PRIMITIVE_SHAPE_OPS: tuple[str, ...] = PRIMITIVE_ROOT_OPS + PRIMITIVE_LOCAL_OPS


def _first_primes(n: int) -> list[int]:
    primes: list[int] = []
    candidate = 2
    while len(primes) < n:
        is_prime = True
        for p in primes:
            if p * p > candidate:
                break
            if candidate % p == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(candidate)
        candidate += 1
    return primes


def _shape_key(shape: Shape):
    return tuple(_shape_key(child) for child in shape)


def normalize_shape(shape: Shape) -> Shape:
    normalized_children = tuple(normalize_shape(child) for child in shape)
    return tuple(sorted(normalized_children, key=_shape_key))


def shape_new(shape: Shape) -> Shape:
    return normalize_shape(shape + ((),))


def shape_drop(shape: Shape) -> Shape:
    if not shape:
        raise ValueError("cannot DROP from an empty root-shape")
    children = list(shape)
    for i, child in enumerate(children):
        if child == ():
            del children[i]
            return normalize_shape(tuple(children))
    raise ValueError("shape_drop requires at least one leaf child at root")


def shape_mass(shape: Shape) -> int:
    shape = normalize_shape(shape)
    return sum(1 + shape_mass(child) for child in shape)


@lru_cache(maxsize=None)
def _shapes_of_mass(mass: int) -> tuple[Shape, ...]:
    if mass < 0:
        raise ValueError("mass must be >= 0")

    if mass == 0:
        return ((),)

    out: set[Shape] = set()

    def _build(remaining: int, min_key, acc: list[Shape]) -> None:
        if remaining == 0:
            out.add(tuple(acc))
            return

        for child_mass in range(remaining):
            weight = 1 + child_mass
            if weight > remaining:
                break

            for child in _shapes_of_mass(child_mass):
                key = _shape_key(child)
                if min_key is not None and key < min_key:
                    continue
                acc.append(child)
                _build(remaining - weight, key, acc)
                acc.pop()

    _build(mass, None, [])
    return tuple(sorted(out, key=_shape_key))


def shape_succ(exp_shape: Shape) -> Shape:
    shape = normalize_shape(exp_shape)
    mass = shape_mass(shape)
    level = _shapes_of_mass(mass)
    idx = level.index(shape)

    if idx + 1 < len(level):
        return level[idx + 1]

    return _shapes_of_mass(mass + 1)[0]


def shape_pred(exp_shape: Shape) -> Shape:
    shape = normalize_shape(exp_shape)
    mass = shape_mass(shape)

    if mass == 0:
        raise ValueError("shape_pred is undefined at exponent-shape for 1")

    level = _shapes_of_mass(mass)
    idx = level.index(shape)

    if idx > 0:
        return level[idx - 1]

    prev_level = _shapes_of_mass(mass - 1)
    return prev_level[-1]


def _replace_at(shape: Shape, path: PathT, op) -> Shape:
    if not path:
        return normalize_shape(op(shape))

    idx = path[0]
    if idx < 0 or idx >= len(shape):
        raise IndexError(f"path index out of range: {idx}")

    children = list(shape)
    children[idx] = _replace_at(children[idx], path[1:], op)
    return normalize_shape(tuple(children))


def shape_inc(shape: Shape, path: PathT) -> Shape:
    if not path:
        raise ValueError("shape_inc requires a non-empty path")
    return _replace_at(normalize_shape(shape), path, shape_succ)


def shape_dec(shape: Shape, path: PathT) -> Shape:
    if not path:
        raise ValueError("shape_dec requires a non-empty path")
    return _replace_at(normalize_shape(shape), path, shape_pred)


def pet_to_shape(tree) -> Shape:
    return normalize_shape(
        tuple(
            () if exp_repr is None else pet_to_shape(exp_repr)
            for _prime, exp_repr in tree
        )
    )


def _exp_gamma(shape: Shape) -> int:
    shape = normalize_shape(shape)
    if shape == ():
        return 1

    child_values = sorted((_exp_gamma(child) for child in shape), reverse=True)
    total = 1
    for prime, exp in zip(_first_primes(len(child_values)), child_values):
        total *= prime ** exp
    return total


def shape_gamma(shape: Shape) -> int:
    shape = normalize_shape(shape)
    if shape == ():
        raise ValueError("shape_gamma is undefined for leaf shape ()")

    child_values = sorted((_exp_gamma(child) for child in shape), reverse=True)
    total = 1
    for prime, exp in zip(_first_primes(len(child_values)), child_values):
        total *= prime ** exp
    return total


def _shape_to_pet(shape: Shape):
    shape = normalize_shape(shape)
    if shape == ():
        raise ValueError("cannot materialize leaf shape () as a root PET")

    children = []
    for child in shape:
        if child == ():
            child_pet = None
            child_value = 1
        else:
            child_pet = _shape_to_pet(child)
            child_value = _exp_gamma(child)
        children.append((child_value, child_pet))

    children.sort(key=lambda item: item[0], reverse=True)

    result = []
    for prime, (_value, exp_repr) in zip(_first_primes(len(children)), children):
        result.append((prime, exp_repr))
    return result


def shape_to_pet(shape: Shape):
    return _shape_to_pet(shape)


def shape_at(shape: Shape, path: PathT) -> Shape:
    node = normalize_shape(shape)
    for idx in path:
        if idx < 0 or idx >= len(node):
            raise IndexError(f"path index out of range: {idx}")
        node = node[idx]
    return node


def shape_paths(shape: Shape, *, include_root: bool = False) -> tuple[PathT, ...]:
    node = normalize_shape(shape)
    out: list[PathT] = []

    def _walk(cur: Shape, path: PathT) -> None:
        out.append(path)
        for i, child in enumerate(cur):
            _walk(child, path + (i,))

    _walk(node, ())
    if include_root:
        return tuple(out)
    return tuple(path for path in out if path)


def shape_neighbors(shape: Shape) -> tuple[dict, ...]:
    root = normalize_shape(shape)
    out: list[dict] = []

    candidates: list[tuple[str, PathT]] = [
        ("NEW", ()),
        ("DROP", ()),
    ]
    candidates.extend(("INC", path) for path in shape_paths(root))
    candidates.extend(("DEC", path) for path in shape_paths(root))

    for op, path in candidates:
        if not shape_can_apply(root, op, path):
            continue
        out.append({
            "op": op,
            "path": path,
            "result": shape_apply(root, op, path),
        })

    seen = set()
    canon = []
    for row in out:
        key = (row["op"], row["path"], row["result"])
        if key in seen:
            continue
        seen.add(key)
        canon.append(row)

    canon.sort(key=lambda row: (row["op"], row["path"], _shape_key(row["result"])))
    return tuple(canon)




def shape_closure(shape: Shape, depth: int) -> tuple[Shape, ...]:
    if depth < 0:
        raise ValueError("depth must be >= 0")

    root = normalize_shape(shape)
    seen = {root}
    frontier = {root}

    for _ in range(depth):
        next_frontier = set()

        for node in frontier:
            for row in shape_neighbors(node):
                result = row["result"]
                if result not in seen:
                    seen.add(result)
                    next_frontier.add(result)

        if not next_frontier:
            break

        frontier = next_frontier

    return tuple(sorted(seen, key=_shape_key))


def shape_frontier_levels(shape: Shape, depth: int) -> tuple[tuple[Shape, ...], ...]:
    if depth < 0:
        raise ValueError("depth must be >= 0")

    root = normalize_shape(shape)
    levels: list[tuple[Shape, ...]] = [(root,)]
    seen = {root}
    frontier = {root}

    for _ in range(depth):
        next_frontier = set()

        for node in frontier:
            for row in shape_neighbors(node):
                result = row["result"]
                if result not in seen:
                    seen.add(result)
                    next_frontier.add(result)

        if not next_frontier:
            break

        level = tuple(sorted(next_frontier, key=_shape_key))
        levels.append(level)
        frontier = set(level)

    return tuple(levels)


def apply_shape_move(shape: Shape, move: dict) -> Shape:
    root = normalize_shape(shape)
    op = move["op"]
    path = move["path"]

    if op == "NEW":
        return shape_new(root)
    if op == "DROP":
        return shape_drop(root)
    if op == "INC":
        return shape_inc(root, path)
    if op == "DEC":
        return shape_dec(root, path)

    raise ValueError(f"unknown shape move op: {op}")


def shape_shortest_path(start: Shape, target: Shape, max_depth: int = 8) -> tuple[dict, ...]:
    if max_depth < 0:
        raise ValueError("max_depth must be >= 0")

    start_n = normalize_shape(start)
    target_n = normalize_shape(target)

    if start_n == target_n:
        return ()

    seen = {start_n}
    parents: dict[Shape, tuple[Shape, dict] | None] = {start_n: None}
    frontier = {start_n}

    for _ in range(max_depth):
        next_frontier = set()

        for node in sorted(frontier, key=_shape_key):
            for move in shape_neighbors(node):
                result = move["result"]
                if result in seen:
                    continue

                seen.add(result)
                parents[result] = (node, move)

                if result == target_n:
                    path = []
                    cur = result
                    while parents[cur] is not None:
                        prev, step = parents[cur]
                        path.append(step)
                        cur = prev
                    path.reverse()
                    return tuple(path)

                next_frontier.add(result)

        if not next_frontier:
            break

        frontier = next_frontier

    raise ValueError(
        f"target shape {target_n!r} not reached from {start_n!r} within max_depth={max_depth}"
    )


def shape_distance(start: Shape, target: Shape, max_depth: int = 8) -> int:
    return len(shape_shortest_path(start, target, max_depth=max_depth))


def index_path_to_stable_path(shape: Shape, path: PathT) -> StablePathT:
    cur = normalize_shape(shape)
    out: list[StableStepT] = []

    for idx in path:
        if idx < 0 or idx >= len(cur):
            raise IndexError(f"path index out of range: {idx}")

        child = cur[idx]
        ordinal = sum(1 for prev in cur[: idx + 1] if prev == child) - 1
        out.append((child, ordinal))
        cur = child

    return tuple(out)


def stable_path_to_index_path(shape: Shape, stable_path: StablePathT) -> PathT:
    cur = normalize_shape(shape)
    out: list[int] = []

    for child_shape, ordinal in stable_path:
        child_shape = normalize_shape(child_shape)
        matches = [i for i, child in enumerate(cur) if child == child_shape]

        if ordinal < 0 or ordinal >= len(matches):
            raise IndexError(
                f"stable path step not resolvable for child={child_shape!r}, ordinal={ordinal}"
            )

        idx = matches[ordinal]
        out.append(idx)
        cur = cur[idx]

    return tuple(out)


def shape_at_stable(shape: Shape, stable_path: StablePathT) -> Shape:
    return shape_at(shape, stable_path_to_index_path(shape, stable_path))


def shape_apply(shape: Shape, op: str, path: PathT = ()) -> Shape:
    root = normalize_shape(shape)
    op = op.upper()

    if op == "NEW":
        if path != ():
            raise ValueError("NEW requires root path ()")
        return shape_new(root)

    if op == "DROP":
        if path != ():
            raise ValueError("DROP requires root path ()")
        return shape_drop(root)

    if op == "INC":
        if path == ():
            raise ValueError("INC requires a non-empty path")
        return shape_inc(root, path)

    if op == "DEC":
        if path == ():
            raise ValueError("DEC requires a non-empty path")
        return shape_dec(root, path)

    raise ValueError(f"unknown shape op: {op}")


def shape_can_apply(shape: Shape, op: str, path: PathT = ()) -> bool:
    try:
        shape_apply(shape, op, path)
        return True
    except (ValueError, IndexError, NotImplementedError):
        return False


def is_primitive_shape_op(op: str) -> bool:
    return op.upper() in PRIMITIVE_SHAPE_OPS


__all__ = [
    # core shape representation
    "Shape",
    "PathT",
    "normalize_shape",
    # primitive rewrite vocabulary
    "PRIMITIVE_ROOT_OPS",
    "PRIMITIVE_LOCAL_OPS",
    "PRIMITIVE_SHAPE_OPS",
    "is_primitive_shape_op",
    # four primitive operations
    "shape_new",
    "shape_drop",
    "shape_inc",
    "shape_dec",
    "shape_apply",
    "shape_can_apply",
    # local successor / predecessor on exponent-shapes
    "shape_succ",
    "shape_pred",
    "shape_mass",
    # shape <-> PET / witness
    "pet_to_shape",
    "shape_to_pet",
    "shape_gamma",
    # path helpers
    "shape_at",
    "shape_paths",
    "index_path_to_stable_path",
    "stable_path_to_index_path",
    "shape_at_stable",
    # exploration helpers
    "shape_neighbors",
    "shape_closure",
    "shape_frontier_levels",
    "shape_shortest_path",
    "shape_distance",
]


def _partial_shape_key(shape) -> tuple:
    if shape is None:
        return (0,)
    return (1, tuple(_partial_shape_key(child) for child in shape))


def normalize_partial_shape(shape):
    if shape is None:
        return None
    normalized_children = tuple(normalize_partial_shape(child) for child in shape)
    return tuple(sorted(normalized_children, key=_partial_shape_key))


def partial_shape_hole_count(shape) -> int:
    if shape is None:
        return 1
    return sum(partial_shape_hole_count(child) for child in shape)


def shape_matches_partial(shape: Shape, partial) -> bool:
    shape = normalize_shape(shape)
    partial = normalize_partial_shape(partial)

    if partial is None:
        return True

    if len(shape) != len(partial):
        return False

    partial_children = list(partial)
    partial_children.sort(key=lambda child: 1 if child is None else 0)

    used = [False] * len(shape)

    def _match(i: int) -> bool:
        if i == len(partial_children):
            return True

        pchild = partial_children[i]

        for j, schild in enumerate(shape):
            if used[j]:
                continue
            if shape_matches_partial(schild, pchild):
                used[j] = True
                if _match(i + 1):
                    return True
                used[j] = False

        return False

    return _match(0)


def partial_shape_is_exact(shape) -> bool:
    if shape is None:
        return False
    return all(partial_shape_is_exact(child) for child in shape)


def _partial_shape_fill_min(shape, *, at_root: bool) -> Shape:
    if shape is None:
        return ((),) if at_root else ()

    return normalize_shape(
        tuple(_partial_shape_fill_min(child, at_root=False) for child in shape)
    )


def partial_shape_fill_min(shape) -> Shape:
    return _partial_shape_fill_min(normalize_partial_shape(shape), at_root=True)


def partial_shape_gamma_min(shape) -> int:
    return shape_gamma(partial_shape_fill_min(shape))


def _partial_shape_fill_neighbors(shape, *, at_root: bool):
    shape = normalize_partial_shape(shape)

    if shape is None:
        return (((),),) if at_root else ((),)

    out = set()

    for i, child in enumerate(shape):
        child_neighbors = _partial_shape_fill_neighbors(child, at_root=False)

        if child is None:
            child_neighbors = ((),)
        elif isinstance(child, tuple):
            child_neighbors = _partial_shape_fill_neighbors(child, at_root=False)
        else:
            child_neighbors = ()

        for new_child in child_neighbors:
            children = list(shape)
            children[i] = new_child
            out.add(normalize_partial_shape(tuple(children)))

    return tuple(sorted(out, key=_partial_shape_key))


def partial_shape_completion_neighbors(shape):
    shape = normalize_partial_shape(shape)

    if partial_shape_is_exact(shape):
        return ()

    if shape is None:
        return (((),),)

    out = set()

    for i, child in enumerate(shape):
        if child is None:
            children = list(shape)
            children[i] = ()
            out.add(normalize_partial_shape(tuple(children)))
            continue

        for new_child in partial_shape_completion_neighbors(child):
            children = list(shape)
            children[i] = new_child
            out.add(normalize_partial_shape(tuple(children)))

    return tuple(sorted(out, key=_partial_shape_key))


def partial_shape_exact_completions(shape):
    root = normalize_partial_shape(shape)

    if partial_shape_is_exact(root):
        return (normalize_shape(root),)

    seen = {root}
    frontier = {root}
    exact = set()

    while frontier:
        next_frontier = set()

        for node in frontier:
            for nxt in partial_shape_completion_neighbors(node):
                if partial_shape_is_exact(nxt):
                    exact.add(normalize_shape(nxt))
                    continue
                if nxt not in seen:
                    seen.add(nxt)
                    next_frontier.add(nxt)

        frontier = next_frontier

    return tuple(sorted(exact, key=_shape_key))


def partial_shape_gamma_exact(shape):
    return tuple(shape_gamma(s) for s in partial_shape_exact_completions(shape))


def partial_shape_shortest_completion_path(shape, target=None):
    start = normalize_partial_shape(shape)

    if partial_shape_is_exact(start):
        exact_start = normalize_shape(start)
        if target is not None and exact_start != normalize_shape(target):
            raise ValueError("exact start shape does not match requested target")
        return (exact_start,)

    if target is None:
        target_set = set(partial_shape_exact_completions(start))
    else:
        target_shape = normalize_shape(target)
        if target_shape not in set(partial_shape_exact_completions(start)):
            raise ValueError("requested target is not an exact completion of the partial shape")
        target_set = {target_shape}

    _ROOT = object()

    seen = {start}
    parents = {start: _ROOT}
    frontier = {start}

    while frontier:
        next_frontier = set()

        for node in sorted(frontier, key=_partial_shape_key):
            for nxt in partial_shape_completion_neighbors(node):
                if nxt in seen:
                    continue

                seen.add(nxt)
                parents[nxt] = node

                if partial_shape_is_exact(nxt) and normalize_shape(nxt) in target_set:
                    path = [normalize_shape(nxt)]
                    cur = node
                    while cur is not _ROOT:
                        path.append(cur)
                        cur = parents[cur]
                    path.reverse()
                    return tuple(path)

                next_frontier.add(nxt)

        frontier = next_frontier

    raise ValueError("no exact completion path found")


def partial_shape_completion_distance(shape, target=None) -> int:
    return len(partial_shape_shortest_completion_path(shape, target=target)) - 1


def partial_shape_shortest_completion_target(shape, target=None) -> Shape:
    path = partial_shape_shortest_completion_path(shape, target=target)
    return normalize_shape(path[-1])


def partial_shape_shortest_completion_gamma(shape, target=None) -> int:
    return shape_gamma(partial_shape_shortest_completion_target(shape, target=target))


def partial_shape_shortest_completion_pet(shape, target=None):
    return shape_to_pet(partial_shape_shortest_completion_target(shape, target=target))


def partial_shape_report(shape) -> dict:
    partial = normalize_partial_shape(shape)
    target = partial_shape_shortest_completion_target(partial)

    return {
        "partial": partial,
        "is_exact": partial_shape_is_exact(partial),
        "hole_count": partial_shape_hole_count(partial),
        "fill_min": partial_shape_fill_min(partial),
        "completion_distance": partial_shape_completion_distance(partial),
        "target_shape": target,
        "target_gamma": shape_gamma(target),
    }
