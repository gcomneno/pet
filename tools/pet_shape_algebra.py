from __future__ import annotations

from typing import TypeAlias

Shape: TypeAlias = tuple["Shape", ...]


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
