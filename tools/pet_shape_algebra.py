from __future__ import annotations

from typing import TypeAlias

Shape: TypeAlias = tuple["Shape", ...]
PathT: TypeAlias = tuple[int, ...]


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


_V0_CHAIN: tuple[Shape, ...] = (
    (),
    ((),),
    ((), ()),
    (((),),),
)


def shape_succ(exp_shape: Shape) -> Shape:
    shape = normalize_shape(exp_shape)
    try:
        idx = _V0_CHAIN.index(shape)
    except ValueError as exc:
        raise NotImplementedError(
            f"shape_succ v0 not defined yet for shape {shape!r}"
        ) from exc

    if idx + 1 >= len(_V0_CHAIN):
        raise NotImplementedError(
            f"shape_succ v0 not defined yet beyond shape {shape!r}"
        )

    return _V0_CHAIN[idx + 1]


def shape_pred(exp_shape: Shape) -> Shape:
    shape = normalize_shape(exp_shape)
    try:
        idx = _V0_CHAIN.index(shape)
    except ValueError as exc:
        raise NotImplementedError(
            f"shape_pred v0 not defined yet for shape {shape!r}"
        ) from exc

    if idx == 0:
        raise ValueError("shape_pred is undefined at exponent-shape for 1")

    return _V0_CHAIN[idx - 1]


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

    # root-level NEW / DROP
    out.append({
        "op": "NEW",
        "path": (),
        "result": shape_new(root),
    })

    try:
        dropped = shape_drop(root)
    except ValueError:
        pass
    else:
        out.append({
            "op": "DROP",
            "path": (),
            "result": dropped,
        })

    # local INC / DEC on every non-root node
    for path in shape_paths(root):
        try:
            inc_result = shape_inc(root, path)
        except (ValueError, NotImplementedError, IndexError):
            pass
        else:
            out.append({
                "op": "INC",
                "path": path,
                "result": inc_result,
            })

        try:
            dec_result = shape_dec(root, path)
        except (ValueError, NotImplementedError, IndexError):
            pass
        else:
            out.append({
                "op": "DEC",
                "path": path,
                "result": dec_result,
            })

    # canonical order, dedup by (op, path, result)
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
