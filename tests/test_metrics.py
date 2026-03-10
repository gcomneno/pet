#!/usr/bin/env python3
from pet import encode, height, leaf_count, max_branching, node_count

def test_metrics_on_known_examples():
    cases = [
        (2, 1, 1, 1, 1),
        (4, 2, 1, 2, 1),
        (12, 3, 2, 2, 2),
        (256, 3, 1, 3, 1),
    ]

    for n, expected_nodes, expected_leaves, expected_height, expected_branching in cases:
        tree = encode(n)
        assert node_count(tree) == expected_nodes, f"node_count failed for {n}"
        assert leaf_count(tree) == expected_leaves, f"leaf_count failed for {n}"
        assert height(tree) == expected_height, f"height failed for {n}"
        assert max_branching(tree) == expected_branching, f"max_branching failed for {n}"


if __name__ == "__main__":
    test_metrics_on_known_examples()
    print("OK")
