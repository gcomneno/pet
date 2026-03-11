from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pet import PET


def _graft(tree: "PET", scion: "PET") -> "PET":
    """Replace every leaf (None exponent) in tree with scion."""
    result = []
    for prime, exp_repr in tree:
        if exp_repr is None:
            result.append((prime, scion))
        else:
            result.append((prime, _graft(exp_repr, scion)))
    return result


def graft(tree: "PET", scion: "PET") -> "PET":
    """Graft scion onto every leaf of tree.

    Every node in tree whose exponent is None (i.e. exponent = 1)
    gets scion as its new exponent subtree.

    The result is always a valid canonical PET representing an integer.

    Example:
        PET(6)  = [(2,•),(3,•)]
        PET(2)  = [(2,•)]
        graft(PET(6), PET(2)) = [(2,[(2,•)]),(3,[(2,•)])] = PET(36)

    Args:
        tree:  the base PET (receives the graft)
        scion: the PET to graft onto every leaf

    Returns:
        A new canonical PET.
    """
    from pet import validate
    validate(tree)
    validate(scion)
    result = _graft(tree, scion)
    validate(result)
    return result

def _node_count(tree) -> int:
    total = 0
    for _, exp_repr in tree:
        total += 1
        if exp_repr is not None:
            total += _node_count(exp_repr)
    return total


def _exp_distance(a_exp, b_exp) -> int:
    if a_exp is None and b_exp is None:
        return 0
    if a_exp is None:
        return _node_count(b_exp)
    if b_exp is None:
        return _node_count(a_exp)
    return _tree_distance(a_exp, b_exp)


def _tree_distance(a, b) -> int:
    a_dict = {p: e for p, e in a}
    b_dict = {p: e for p, e in b}
    all_primes = set(a_dict) | set(b_dict)

    dist = 0
    for p in all_primes:
        if p in a_dict and p in b_dict:
            dist += _exp_distance(a_dict[p], b_dict[p])
        elif p in a_dict:
            dist += 1 + (0 if a_dict[p] is None else _node_count(a_dict[p]))
        else:
            dist += 1 + (0 if b_dict[p] is None else _node_count(b_dict[p]))
    return dist


def distance(a, b) -> int:
    """Return the structural distance between two canonical PETs.

    Distance is defined recursively:
    - primes present in one tree but not the other contribute
      their full subtree node count
    - primes present in both trees contribute the recursive
      distance between their exponent subtrees
    - two leaves (None) have distance 0

    The result is 0 if and only if the two PETs are identical.
    """
    from pet import validate
    validate(a)
    validate(b)
    return _tree_distance(a, b)


def _shape(tree) -> tuple:
    """Return the structural shape of a PET, ignoring prime values."""
    if tree is None:
        return None
    return tuple(sorted((_shape(exp) for _, exp in tree), key=lambda x: x or ()))

def _shape_node_count(shape) -> int:
    if shape is None:
        return 0
    return 1 + sum(_shape_node_count(s) for s in shape)


def _structural_distance(shape_a, shape_b) -> int:
    if shape_a == shape_b:
        return 0
    if shape_a is None:
        return _shape_node_count(shape_b)
    if shape_b is None:
        return _shape_node_count(shape_a)

    # match children greedily by sorted order
    children_a = sorted(shape_a, key=lambda x: x or ())
    children_b = sorted(shape_b, key=lambda x: x or ())

    dist = 0
    i, j = 0, 0
    while i < len(children_a) and j < len(children_b):
        dist += _structural_distance(children_a[i], children_b[j])
        i += 1
        j += 1
    while i < len(children_a):
        dist += 1 + _shape_node_count(children_a[i])
        i += 1
    while j < len(children_b):
        dist += 1 + _shape_node_count(children_b[j])
        j += 1
    return dist


def structural_distance(a, b) -> int:
    """Return the structural distance between two PETs, ignoring prime values.

    Two PETs have structural distance 0 if and only if they are
    isomorphic as ordered trees, regardless of which primes appear.

    Example:
        PET(4) = [(2,[(2,•)])]  and  PET(9) = [(3,[(2,•)])]
        are structurally identical -> structural_distance = 0
    """
    from pet import validate
    validate(a)
    validate(b)
    return _structural_distance(_shape(a), _shape(b))
