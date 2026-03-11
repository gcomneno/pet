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
