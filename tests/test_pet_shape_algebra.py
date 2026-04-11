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
