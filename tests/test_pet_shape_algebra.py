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
