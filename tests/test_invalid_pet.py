#!/usr/bin/env python3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pet import from_jsonable, validate


def assert_invalid(tree):
    with pytest.raises((TypeError, ValueError)):
        validate(tree)


def test_validate_rejects_invalid_roots():
    for tree in [None, 123, "not-a-pet", {"p": 2, "e": None}]:
        assert_invalid(tree)


def test_validate_rejects_invalid_node_shapes():
    for tree in [[2, None], [(2,)], [(2, None, 7)], ["not-a-node"]]:
        assert_invalid(tree)


def test_validate_rejects_non_prime_bases():
    for tree in [[(1, None)], [(0, None)], [(-3, None)], [(4, None)]]:
        assert_invalid(tree)


def test_validate_rejects_non_integer_prime_bases():
    for tree in [[("2", None)], [(2.0, None)], [(True, None)]]:
        assert_invalid(tree)


def test_validate_rejects_invalid_exponent_payloads():
    for tree in [[(2, 3)], [(2, "x")], [(2, {})]]:
        assert_invalid(tree)


def test_validate_rejects_non_canonical_prime_order():
    for tree in [[(3, None), (2, None)], [(2, None), (2, None)]]:
        assert_invalid(tree)


def test_validate_rejects_invalid_subtrees():
    for tree in [[(2, [(4, None)])], [(2, [(3, 5)])], [(2, [(3, None), (2, None)])]]:
        assert_invalid(tree)


def test_from_jsonable_rejects_invalid_json_shapes():
    invalid = [
        None, 123, "not-a-pet", {"p": 2, "e": None},
        [{"p": 2}], [{"e": None}], [{"p": 2, "e": None, "extra": 1}],
        [{"p": "2", "e": None}], [{"p": 4, "e": None}], [{"p": 2, "e": 3}],
    ]
    for value in invalid:
        with pytest.raises((TypeError, ValueError)):
            from_jsonable(value)
