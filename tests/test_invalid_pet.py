#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pet import from_jsonable, validate


def assert_invalid(tree):
    try:
        validate(tree)
    except (TypeError, ValueError):
        return
    raise AssertionError(
        f"Expected TypeError or ValueError for invalid tree: {tree!r}"
    )


def test_validate_rejects_invalid_roots():
    invalid_roots = [
        None,
        123,
        "not-a-pet",
        {"p": 2, "e": None},
    ]
    for tree in invalid_roots:
        assert_invalid(tree)


def test_validate_rejects_invalid_node_shapes():
    invalid_trees = [
        [2, None],
        [(2,)],
        [(2, None, 7)],
        ["not-a-node"],
    ]
    for tree in invalid_trees:
        assert_invalid(tree)


def test_validate_rejects_non_prime_bases():
    invalid_trees = [
        [(1, None)],
        [(0, None)],
        [(-3, None)],
        [(4, None)],
    ]
    for tree in invalid_trees:
        assert_invalid(tree)


def test_validate_rejects_non_integer_prime_bases():
    invalid_trees = [
        [("2", None)],
        [(2.0, None)],
        [(True, None)],
    ]
    for tree in invalid_trees:
        assert_invalid(tree)


def test_validate_rejects_invalid_exponent_payloads():
    invalid_trees = [
        [(2, 3)],
        [(2, "x")],
        [(2, {})],
    ]
    for tree in invalid_trees:
        assert_invalid(tree)


def test_validate_rejects_non_canonical_prime_order():
    invalid_trees = [
        [(3, None), (2, None)],
        [(2, None), (2, None)],
    ]
    for tree in invalid_trees:
        assert_invalid(tree)


def test_validate_rejects_invalid_subtrees():
    invalid_trees = [
        [(2, [(4, None)])],
        [(2, [(3, 5)])],
        [(2, [(3, None), (2, None)])],
    ]
    for tree in invalid_trees:
        assert_invalid(tree)


def test_from_jsonable_rejects_invalid_json_shapes():
    invalid_json_values = [
        None,
        123,
        "not-a-pet",
        {"p": 2, "e": None},
        [{"p": 2}],
        [{"e": None}],
        [{"p": 2, "e": None, "extra": 1}],
        [{"p": "2", "e": None}],
        [{"p": 4, "e": None}],
        [{"p": 2, "e": 3}],
    ]
    for value in invalid_json_values:
        try:
            from_jsonable(value)
        except (TypeError, ValueError):
            continue
        raise AssertionError(
            f"Expected TypeError or ValueError for invalid JSON value: {value!r}"
        )


if __name__ == "__main__":
    test_validate_rejects_invalid_roots()
    test_validate_rejects_invalid_node_shapes()
    test_validate_rejects_non_prime_bases()
    test_validate_rejects_non_integer_prime_bases()
    test_validate_rejects_invalid_exponent_payloads()
    test_validate_rejects_non_canonical_prime_order()
    test_validate_rejects_invalid_subtrees()
    test_from_jsonable_rejects_invalid_json_shapes()
    print("OK")
