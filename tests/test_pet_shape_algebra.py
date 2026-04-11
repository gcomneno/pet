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
