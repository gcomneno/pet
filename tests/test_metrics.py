#!/usr/bin/env python3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pet import (
    branch_profile,
    encode,
    height,
    leaf_count,
    max_branching,
    node_count,
    recursive_mass,
)

@pytest.mark.parametrize("n, expected_nodes, expected_leaves, expected_height, expected_branching, expected_profile, expected_mass", [
    (2,   1, 1, 1, 1, [1],       0),
    (4,   2, 1, 2, 1, [1, 1],    1),
    (12,  3, 2, 2, 2, [2, 1],    1),
    (256, 3, 1, 3, 1, [1, 1, 1], 2),
    (72,  4, 2, 2, 2, [2, 2],    2),
    (360, 5, 3, 2, 3, [3, 2],    2),
])
def test_metrics(n, expected_nodes, expected_leaves, expected_height, expected_branching, expected_profile, expected_mass):
    tree = encode(n)
    assert node_count(tree)    == expected_nodes,    f"node_count failed for {n}"
    assert leaf_count(tree)    == expected_leaves,   f"leaf_count failed for {n}"
    assert height(tree)        == expected_height,   f"height failed for {n}"
    assert max_branching(tree) == expected_branching,f"max_branching failed for {n}"
    assert branch_profile(tree)== expected_profile,  f"branch_profile failed for {n}"
    assert recursive_mass(tree)== expected_mass,     f"recursive_mass failed for {n}"
