from tools.partial_signature_probe import (
    _classify_residual,
    _exp_signature_data,
    _residual_lower_bound_children,
    _root_generator_from_children,
)


def test_open_composite_residual_adds_two_leaf_children_to_known_squarefree_prefix() -> None:
    exp1 = _exp_signature_data(1)
    assert exp1["generator"] == 1
    assert exp1["signature"] == []

    known_children = [exp1["signature"] for _ in range(4)]
    assert known_children == [[], [], [], []]
    assert _root_generator_from_children(known_children) == 210

    residual_info = _classify_residual(29 * 31)
    assert residual_info["status"] == "composite-non-prime-power"
    assert residual_info["root_children_lower_bound"] == 2
    assert residual_info["exact_root_children"] is None

    residual_lb_children = _residual_lower_bound_children(residual_info)
    assert residual_lb_children == [[], []]

    assert _root_generator_from_children(known_children + residual_lb_children) == 30030
