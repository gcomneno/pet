from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pet.core import encode, validate
from tools.pathwise_one_step_probe import apply_rw
from tools.pathwise_first_bad_ancestor_probe import (
    classify_pathwise_rewrite,
    score_pathwise_move,
)


def test_score_prefers_embedded_failure_over_root_failure_for_same_local_growth():
    root0 = encode(36)
    root1 = apply_rw(root0, (1,), 0, 2)
    info_root = classify_pathwise_rewrite(root0, root1, (1,))

    emb0 = [
        (2, encode(324)),
        (3, encode(36)),
        (5, None),
    ]
    validate(emb0)
    emb1 = apply_rw(emb0, (1, 1), 0, 2)
    validate(emb1)
    info_emb = classify_pathwise_rewrite(emb0, emb1, (1, 1))

    assert score_pathwise_move(root0, root1, (1,), info_root) < score_pathwise_move(emb0, emb1, (1, 1), info_emb)


def test_score_prefers_no_failure_over_embedded_failure():
    ok0 = encode(12)
    ok1 = apply_rw(ok0, (), 0, 4)
    info_ok = classify_pathwise_rewrite(ok0, ok1, ())

    emb0 = [
        (2, encode(324)),
        (3, encode(36)),
        (5, None),
    ]
    validate(emb0)
    emb1 = apply_rw(emb0, (1, 1), 0, 2)
    validate(emb1)
    info_emb = classify_pathwise_rewrite(emb0, emb1, (1, 1))

    assert info_ok["failure_kind"] is None
    assert score_pathwise_move(ok0, ok1, (), info_ok) > score_pathwise_move(emb0, emb1, (1, 1), info_emb)
