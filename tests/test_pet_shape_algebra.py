from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def test_shape_new_and_drop_roundtrip_on_root_children():
    from tools.pet_shape_algebra import normalize_shape, shape_new, shape_drop

    base = normalize_shape(((), ((),)))
    grown = shape_new(base)

    assert grown == normalize_shape(((), (), ((),)))
    assert shape_drop(grown) == base


def test_shape_succ_small_chain():
    from tools.pet_shape_algebra import shape_succ

    assert shape_succ(()) == ((),)
    assert shape_succ(((),)) == ((), ())
    assert shape_succ(((), ())) == (((),),)


def test_shape_pred_inverts_shape_succ_on_small_chain():
    from tools.pet_shape_algebra import shape_pred, shape_succ

    samples = [
        (),
        ((),),
        ((), ()),
        (((),),),
    ]

    for shape in samples[:-1]:
        assert shape_pred(shape_succ(shape)) == shape


def test_shape_inc_and_dec_roundtrip_on_single_root_child():
    from tools.pet_shape_algebra import normalize_shape, shape_dec, shape_inc

    base = normalize_shape(((),))
    grown = shape_inc(base, (0,))

    assert grown == normalize_shape((((),),))
    assert shape_dec(grown, (0,)) == base


def test_shape_inc_and_dec_roundtrip_on_deep_chain():
    from tools.pet_shape_algebra import normalize_shape, shape_dec, shape_inc

    base = normalize_shape(((((),),),))
    grown = shape_inc(base, (0, 0, 0))

    assert grown == normalize_shape((((((),),),),))
    assert shape_dec(grown, (0, 0, 0)) == base


def test_pet_to_shape_small_numbers():
    from pet.core import encode
    from tools.pet_shape_algebra import pet_to_shape

    assert pet_to_shape(encode(2)) == ((),)
    assert pet_to_shape(encode(3)) == ((),)
    assert pet_to_shape(encode(4)) == (((),),)
    assert pet_to_shape(encode(6)) == ((), ())
    assert pet_to_shape(encode(8)) == (((),),)


def test_shape_gamma_small_shapes():
    from tools.pet_shape_algebra import shape_gamma

    assert shape_gamma(((),)) == 2
    assert shape_gamma(((), ())) == 6
    assert shape_gamma((((),),)) == 4
    assert shape_gamma(((), ((),))) == 12


def test_shape_to_pet_roundtrip_via_pet_to_shape():
    from pet.core import decode
    from tools.pet_shape_algebra import pet_to_shape, shape_gamma, shape_to_pet

    shapes = [
        ((),),
        ((), ()),
        (((),),),
        ((), ((),)),
    ]

    for shape in shapes:
        pet = shape_to_pet(shape)
        assert pet_to_shape(pet) == shape
        assert decode(pet) == shape_gamma(shape)


def test_shape_gamma_matches_core_shape_generator_on_small_sample():
    from pet.core import encode, shape_generator
    from tools.pet_shape_algebra import pet_to_shape, shape_gamma

    sample = [2, 3, 4, 6, 8, 12, 18, 24, 36, 72]

    for n in sample:
        assert shape_gamma(pet_to_shape(encode(n))) == shape_generator(n)


def test_shape_to_pet_materializes_core_generator_on_small_sample():
    from pet.core import decode, encode, shape_generator
    from tools.pet_shape_algebra import pet_to_shape, shape_to_pet

    sample = [2, 3, 4, 6, 8, 12, 18, 24, 36, 72]

    for n in sample:
        shape = pet_to_shape(encode(n))
        assert decode(shape_to_pet(shape)) == shape_generator(n)


def test_shape_at_reads_deep_node():
    from tools.pet_shape_algebra import normalize_shape, shape_at

    shape = normalize_shape(((((),),),))
    assert shape_at(shape, ()) == shape
    assert shape_at(shape, (0,)) == (((),),)
    assert shape_at(shape, (0, 0)) == ((),)
    assert shape_at(shape, (0, 0, 0)) == ()


def test_shape_paths_lists_all_nodes():
    from tools.pet_shape_algebra import normalize_shape, shape_paths

    shape = normalize_shape(((), ((),)))
    assert shape_paths(shape) == ((0,), (1,), (1, 0))
    assert shape_paths(shape, include_root=True) == ((), (0,), (1,), (1, 0))


def test_shape_neighbors_for_single_leaf_child():
    from tools.pet_shape_algebra import normalize_shape, shape_neighbors

    shape = normalize_shape(((),))
    moves = shape_neighbors(shape)

    got = {(row["op"], row["path"], row["result"]) for row in moves}
    expected = {
        ("NEW", (), normalize_shape(((), ()))),
        ("DROP", (), normalize_shape(())),
        ("INC", (0,), normalize_shape((((),),))),
    }

    assert got == expected


def test_shape_neighbors_for_single_recursive_child():
    from tools.pet_shape_algebra import normalize_shape, shape_neighbors

    shape = normalize_shape((((),),))
    moves = shape_neighbors(shape)

    got = {(row["op"], row["path"], row["result"]) for row in moves}
    expected = {
        ("NEW", (), normalize_shape(((), ((),)))),
        ("INC", (0,), normalize_shape((((), ()),))),
        ("INC", (0, 0), normalize_shape(((((),),),))),
        ("DEC", (0,), normalize_shape(((),))),
    }

    assert got == expected


def test_shape_closure_depth_zero_returns_only_root():
    from tools.pet_shape_algebra import normalize_shape, shape_closure

    shape = normalize_shape(((),))
    assert shape_closure(shape, 0) == (shape,)


def test_shape_closure_depth_one_matches_immediate_reachable_shapes():
    from tools.pet_shape_algebra import normalize_shape, shape_closure

    shape = normalize_shape(((),))
    got = set(shape_closure(shape, 1))
    expected = {
        normalize_shape(((),)),
        normalize_shape(()),
        normalize_shape(((), ())),
        normalize_shape((((),),)),
    }

    assert got == expected


def test_shape_closure_normalizes_input_shape():
    from tools.pet_shape_algebra import shape_closure

    got = set(shape_closure((((),), ()), 0))
    expected = { ((), ((),)) }

    assert got == expected


def test_shape_frontier_levels_depth_zero():
    from tools.pet_shape_algebra import normalize_shape, shape_frontier_levels

    shape = normalize_shape(((),))
    assert shape_frontier_levels(shape, 0) == ((shape,),)


def test_shape_frontier_levels_depth_one_from_single_leaf_child():
    from tools.pet_shape_algebra import normalize_shape, shape_frontier_levels

    shape = normalize_shape(((),))
    levels = shape_frontier_levels(shape, 1)

    assert levels[0] == (shape,)
    assert set(levels[1]) == {
        normalize_shape(()),
        normalize_shape(((), ())),
        normalize_shape((((),),)),
    }


def test_shape_frontier_levels_depth_two_has_no_duplicates_across_levels():
    from tools.pet_shape_algebra import normalize_shape, shape_frontier_levels

    shape = normalize_shape(((),))
    levels = shape_frontier_levels(shape, 2)

    flat = [node for level in levels for node in level]
    assert len(flat) == len(set(flat))


def test_shape_shortest_path_identity_is_empty():
    from tools.pet_shape_algebra import normalize_shape, shape_shortest_path

    shape = normalize_shape(((),))
    assert shape_shortest_path(shape, shape) == ()


def test_shape_shortest_path_single_step_inc():
    from tools.pet_shape_algebra import (
        apply_shape_move,
        normalize_shape,
        shape_shortest_path,
    )

    start = normalize_shape(((),))
    target = normalize_shape((((),),))

    path = shape_shortest_path(start, target, max_depth=2)

    assert len(path) == 1
    assert path[0]["op"] == "INC"
    assert path[0]["path"] == (0,)
    assert apply_shape_move(start, path[0]) == target


def test_shape_shortest_path_single_step_drop():
    from tools.pet_shape_algebra import (
        apply_shape_move,
        normalize_shape,
        shape_shortest_path,
    )

    start = normalize_shape(((),))
    target = normalize_shape(())

    path = shape_shortest_path(start, target, max_depth=2)

    assert len(path) == 1
    assert path[0]["op"] == "DROP"
    assert path[0]["path"] == ()
    assert apply_shape_move(start, path[0]) == target


def test_shape_shortest_path_two_steps_to_root_new_then_inc():
    from tools.pet_shape_algebra import (
        apply_shape_move,
        normalize_shape,
        shape_shortest_path,
    )

    start = normalize_shape(())
    target = normalize_shape((((),),))

    path = shape_shortest_path(start, target, max_depth=3)

    cur = start
    for step in path:
        cur = apply_shape_move(cur, step)

    assert cur == target
    assert len(path) == 2


def test_shape_distance_identity_is_zero():
    from tools.pet_shape_algebra import normalize_shape, shape_distance

    shape = normalize_shape(((),))
    assert shape_distance(shape, shape) == 0


def test_shape_distance_single_step_cases():
    from tools.pet_shape_algebra import normalize_shape, shape_distance

    assert shape_distance(normalize_shape(((),)), normalize_shape(()), max_depth=2) == 1
    assert shape_distance(normalize_shape(((),)), normalize_shape((((),),)), max_depth=2) == 1


def test_shape_distance_two_step_case():
    from tools.pet_shape_algebra import normalize_shape, shape_distance

    start = normalize_shape(())
    target = normalize_shape((((),),))
    assert shape_distance(start, target, max_depth=3) == 2


def test_shape_succ_moves_past_old_hardcoded_prefix():
    from tools.pet_shape_algebra import shape_succ

    assert shape_succ((((),),)) == ((), (), ())


def test_shape_pred_inverts_extended_successor_step():
    from tools.pet_shape_algebra import shape_pred, shape_succ

    shape = (((),),)
    assert shape_pred(shape_succ(shape)) == shape


def test_stable_path_roundtrip_on_duplicate_leaf_siblings():
    from tools.pet_shape_algebra import (
        index_path_to_stable_path,
        normalize_shape,
        stable_path_to_index_path,
    )

    shape = normalize_shape(((), (), ((),)))
    path = (1,)

    stable = index_path_to_stable_path(shape, path)

    assert stable == (((), 1),)
    assert stable_path_to_index_path(shape, stable) == path


def test_stable_path_roundtrip_on_duplicate_recursive_siblings():
    from tools.pet_shape_algebra import (
        index_path_to_stable_path,
        normalize_shape,
        stable_path_to_index_path,
    )

    shape = normalize_shape((((),), ((),), ((), ())))
    path = (1, 0)

    stable = index_path_to_stable_path(shape, path)

    assert stable == ((((),), 1), ((), 0))
    assert stable_path_to_index_path(shape, stable) == path


def test_shape_at_stable_reads_same_node_as_shape_at():
    from tools.pet_shape_algebra import (
        index_path_to_stable_path,
        normalize_shape,
        shape_at,
        shape_at_stable,
    )

    shape = normalize_shape((((),), ((),), ((), ())))
    path = (2, 1)
    stable = index_path_to_stable_path(shape, path)

    assert shape_at_stable(shape, stable) == shape_at(shape, path)


def test_shape_apply_dispatches_all_four_primitives():
    from tools.pet_shape_algebra import normalize_shape, shape_apply

    assert shape_apply(normalize_shape(((),)), "NEW") == normalize_shape(((), ()))
    assert shape_apply(normalize_shape(((),)), "DROP") == normalize_shape(())
    assert shape_apply(normalize_shape(((),)), "INC", (0,)) == normalize_shape((((),),))
    assert shape_apply(normalize_shape((((),),)), "DEC", (0,)) == normalize_shape(((),))


def test_shape_apply_rejects_bad_root_usage():
    import pytest
    from tools.pet_shape_algebra import normalize_shape, shape_apply

    shape = normalize_shape(((),))

    with pytest.raises(ValueError):
        shape_apply(shape, "NEW", (0,))

    with pytest.raises(ValueError):
        shape_apply(shape, "DROP", (0,))

    with pytest.raises(ValueError):
        shape_apply(shape, "INC", ())

    with pytest.raises(ValueError):
        shape_apply(shape, "DEC", ())


def test_shape_can_apply_reports_basic_cases():
    from tools.pet_shape_algebra import normalize_shape, shape_can_apply

    assert shape_can_apply(normalize_shape(((),)), "NEW")
    assert shape_can_apply(normalize_shape(((),)), "DROP")
    assert shape_can_apply(normalize_shape(((),)), "INC", (0,))
    assert shape_can_apply(normalize_shape((((),),)), "DEC", (0,))

    assert not shape_can_apply(normalize_shape(()), "DROP")
    assert not shape_can_apply(normalize_shape(((),)), "INC", ())
    assert not shape_can_apply(normalize_shape(((),)), "NOPE")


def test_shape_neighbors_matches_dispatcher_results():
    from tools.pet_shape_algebra import (
        normalize_shape,
        shape_apply,
        shape_can_apply,
        shape_neighbors,
        shape_paths,
    )

    shape = normalize_shape((((),),))
    got = {(row["op"], row["path"], row["result"]) for row in shape_neighbors(shape)}

    expected = set()
    candidates = [("NEW", ()), ("DROP", ())]
    candidates.extend(("INC", path) for path in shape_paths(shape))
    candidates.extend(("DEC", path) for path in shape_paths(shape))

    for op, path in candidates:
        if shape_can_apply(shape, op, path):
            expected.add((op, path, shape_apply(shape, op, path)))

    assert got == expected


def test_primitive_shape_op_sets_are_exactly_the_four_core_ops():
    from tools.pet_shape_algebra import (
        PRIMITIVE_LOCAL_OPS,
        PRIMITIVE_ROOT_OPS,
        PRIMITIVE_SHAPE_OPS,
    )

    assert PRIMITIVE_ROOT_OPS == ("NEW", "DROP")
    assert PRIMITIVE_LOCAL_OPS == ("INC", "DEC")
    assert PRIMITIVE_SHAPE_OPS == ("NEW", "DROP", "INC", "DEC")


def test_is_primitive_shape_op_accepts_only_core_ops():
    from tools.pet_shape_algebra import is_primitive_shape_op

    assert is_primitive_shape_op("NEW")
    assert is_primitive_shape_op("DROP")
    assert is_primitive_shape_op("INC")
    assert is_primitive_shape_op("DEC")
    assert is_primitive_shape_op("new")
    assert not is_primitive_shape_op("SUCC")
    assert not is_primitive_shape_op("PRED")
    assert not is_primitive_shape_op("NOPE")


def test_shape_neighbors_emit_only_primitive_ops():
    from tools.pet_shape_algebra import (
        PRIMITIVE_SHAPE_OPS,
        normalize_shape,
        shape_neighbors,
    )

    shape = normalize_shape((((),),))
    assert {row["op"] for row in shape_neighbors(shape)} <= set(PRIMITIVE_SHAPE_OPS)


def test_normalize_partial_shape_sorts_known_children_and_holes():
    from tools.pet_shape_algebra import normalize_partial_shape

    partial = (((),), None, ())
    assert normalize_partial_shape(partial) == (None, (), ((),))


def test_partial_shape_hole_count_counts_unknown_subtrees():
    from tools.pet_shape_algebra import partial_shape_hole_count

    assert partial_shape_hole_count(None) == 1
    assert partial_shape_hole_count((None, (), (None,))) == 2


def test_shape_matches_partial_for_exact_and_unknown_cases():
    from tools.pet_shape_algebra import normalize_shape, shape_matches_partial

    assert shape_matches_partial(normalize_shape(((),)), None)
    assert shape_matches_partial(normalize_shape(((), ())), (None, ()))
    assert shape_matches_partial(normalize_shape((((),),)), ((None,),))
    assert not shape_matches_partial(normalize_shape(((),)), ((), ()))
    assert not shape_matches_partial(normalize_shape(((), ())), (((),), ()))


def test_shape_matches_partial_on_small_core_generators():
    from pet.core import encode
    from tools.pet_shape_algebra import pet_to_shape, shape_matches_partial

    assert shape_matches_partial(pet_to_shape(encode(6)), ((), ()))
    assert shape_matches_partial(pet_to_shape(encode(12)), ((), None))
    assert not shape_matches_partial(pet_to_shape(encode(8)), ((), ()))
