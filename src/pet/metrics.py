from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pet.core import PET


def verticality_ratio(tree: "PET") -> float:
    """Return the ratio height / node_count.

    Ranges from 1.0 (perfectly linear chain) down toward 0.0
    (wide, flat tree with many nodes at the same level).
    """
    from pet.core import height, node_count, validate
    validate(tree)
    return height(tree) / node_count(tree)


def structural_asymmetry(tree: "PET") -> float:
    """Return the standard deviation of the branch profile.

    A value of 0.0 means the tree has the same number of nodes
    at every level (perfectly uniform). Higher values indicate
    irregular, asymmetric branching across levels.
    """
    from pet.core import branch_profile, validate
    validate(tree)

    profile = branch_profile(tree)
    n = len(profile)
    if n <= 1:
        return 0.0

    mean = sum(profile) / n
    variance = sum((x - mean) ** 2 for x in profile) / n
    return variance ** 0.5


def subtree_mixing_score(tree: "PET") -> float:
    """Return an experimental score for local subtree mixing.

    This is a research/extended metric, not part of the canonical metric set.
    It is intended to explore whether locally mixed child-subtree structure
    can distinguish rare collisions between different unordered PET shapes.
    """
    from pet.algebra import _shape
    from pet.core import validate

    validate(tree)

    def _score(subtree: "PET") -> int:
        total = 0

        for _, exp_repr in subtree:
            if exp_repr is None:
                continue

            child_shapes = [_shape(child_exp) for _, child_exp in exp_repr]
            total += len(set(child_shapes)) - 1
            total += _score(exp_repr)

        return total

    return float(_score(tree))


def extended_metrics(tree: "PET") -> dict:
    """Return all base metrics plus extra/research metrics."""
    from pet.core import metrics_dict
    base = metrics_dict(tree)
    base["verticality_ratio"] = verticality_ratio(tree)
    base["structural_asymmetry"] = structural_asymmetry(tree)
    base["subtree_mixing_score"] = subtree_mixing_score(tree)
    return base


def is_linear(tree: "PET") -> bool:
    """Return True if the PET is a pure linear chain (max_branching == 1)."""
    from pet.core import max_branching, validate
    validate(tree)
    return max_branching(tree) == 1


def is_level_uniform(tree: "PET") -> bool:
    """Return True if every level of the PET has the same number of nodes.

    This is equivalent to structural_asymmetry == 0.0.
    Note: is_linear is the special case where max_branching == 1.
    """
    from pet.core import branch_profile, validate
    validate(tree)
    profile = branch_profile(tree)
    return len(set(profile)) == 1


def is_expanding(tree: "PET") -> bool:
    """Return True if the last level of the PET has more nodes than the first.

    This is a rare structural property — it occurs when at least one
    exponent subtree branches at the second level (i.e. the exponent
    itself has two or more distinct prime factors).
    """
    from pet.core import branch_profile, validate
    validate(tree)
    profile = branch_profile(tree)
    return len(profile) >= 2 and profile[-1] > profile[0]


def is_squarefree(tree: "PET") -> bool:
    """Return True if the PET has recursive_mass == 0.

    Equivalent to: all exponents in the factorization are 1,
    i.e. the number is squarefree.
    All nodes in the tree are at depth 0 (root level only).
    """
    from pet.core import recursive_mass, validate
    validate(tree)
    return recursive_mass(tree) == 0


def leaf_ratio(tree: "PET"):
    """Return the ratio leaf_count / node_count as an exact Fraction.

    This ratio is always rational and belongs to a sparse discrete set.
    Known families:
    - 1/k  for chains of height k (profile [1,1,...,1])
    - k/(k+1)  for flat trees with one recursive node (profile [k,1])
    - k/(2k+1)  for two-level uniform trees (profile [k,k,1])
    """
    from fractions import Fraction
    from pet.core import leaf_count, node_count, validate
    validate(tree)
    return Fraction(leaf_count(tree), node_count(tree))


def profile_shape(tree: "PET") -> str:
    """Classify the morphology of the branch profile.

    Returns one of:
    - 'point'      — single node (height 1)
    - 'linear'     — all levels have exactly 1 node
    - 'expanding'  — last level has more nodes than first
    - 'bell'       — peak is at an internal level (not first or last)
    - 'normal'     — none of the above (typical contracting shape)
    """
    from pet.core import branch_profile, validate
    validate(tree)
    profile = branch_profile(tree)

    if len(profile) == 1:
        return 'point'
    if all(x == 1 for x in profile):
        return 'linear'
    if profile[-1] > profile[0]:
        return 'expanding'
    if len(profile) >= 3:
        peak = max(range(len(profile)), key=lambda i: profile[i])
        if 0 < peak < len(profile) - 1:
            return 'bell'
    return 'normal'
