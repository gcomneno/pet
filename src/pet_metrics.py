from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pet import PET


def verticality_ratio(tree: "PET") -> float:
    """Return the ratio height / node_count.

    Ranges from 1.0 (perfectly linear chain) down toward 0.0
    (wide, flat tree with many nodes at the same level).
    """
    from pet import height, node_count, validate
    validate(tree)
    return height(tree) / node_count(tree)


def structural_asymmetry(tree: "PET") -> float:
    """Return the standard deviation of the branch profile.

    A value of 0.0 means the tree has the same number of nodes
    at every level (perfectly uniform). Higher values indicate
    irregular, asymmetric branching across levels.
    """
    from pet import branch_profile, validate
    validate(tree)

    profile = branch_profile(tree)
    n = len(profile)
    if n <= 1:
        return 0.0

    mean = sum(profile) / n
    variance = sum((x - mean) ** 2 for x in profile) / n
    return variance ** 0.5


def extended_metrics(tree: "PET") -> dict:
    """Return all base metrics plus verticality_ratio and structural_asymmetry."""
    from pet import metrics_dict
    base = metrics_dict(tree)
    base["verticality_ratio"] = verticality_ratio(tree)
    base["structural_asymmetry"] = structural_asymmetry(tree)
    return base


def is_linear(tree: "PET") -> bool:
    """Return True if the PET is a pure linear chain (max_branching == 1)."""
    from pet import max_branching, validate
    validate(tree)
    return max_branching(tree) == 1


def is_level_uniform(tree: "PET") -> bool:
    """Return True if every level of the PET has the same number of nodes.

    This is equivalent to structural_asymmetry == 0.0.
    Note: is_linear is the special case where max_branching == 1.
    """
    from pet import branch_profile, validate
    validate(tree)
    profile = branch_profile(tree)
    return len(set(profile)) == 1


def is_expanding(tree: "PET") -> bool:
    """Return True if the last level of the PET has more nodes than the first.

    This is a rare structural property — it occurs when at least one
    exponent subtree branches at the second level (i.e. the exponent
    itself has two or more distinct prime factors).
    """
    from pet import branch_profile, validate
    validate(tree)
    profile = branch_profile(tree)
    return len(profile) >= 2 and profile[-1] > profile[0]


def is_squarefree(tree: "PET") -> bool:
    """Return True if the PET has recursive_mass == 0.

    Equivalent to: all exponents in the factorization are 1,
    i.e. the number is squarefree.
    All nodes in the tree are at depth 0 (root level only).
    """
    from pet import recursive_mass, validate
    validate(tree)
    return recursive_mass(tree) == 0
