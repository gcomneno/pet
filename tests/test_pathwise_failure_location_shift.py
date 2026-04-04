from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pet.core import encode, validate
from tools.pathwise_one_step_probe import apply_rw
from tools.pathwise_first_bad_ancestor_probe import classify_pathwise_rewrite


def test_same_local_rewrite_shifts_failure_location_when_root_ceiling_absorbs_growth():
    # standalone witness: root fails
    root0 = encode(36)
    root1 = apply_rw(root0, (1,), 0, 2)
    info_root = classify_pathwise_rewrite(root0, root1, (1,))

    # explicit canonical embedding: root absorbs, embedded parent fails
    emb0 = [
        (2, encode(324)),
        (3, encode(36)),
        (5, None),
    ]
    validate(emb0)

    emb1 = apply_rw(emb0, (1, 1), 0, 2)
    validate(emb1)
    info_emb = classify_pathwise_rewrite(emb0, emb1, (1, 1))

    assert info_root["local_ok"] is True
    assert info_emb["local_ok"] is True

    assert info_root["failure_kind"] == "root"
    assert info_root["first_bad_path"] == ()
    assert info_root["first_violation"]["path"] == ()

    assert info_emb["failure_kind"] == "embedded_ancestor"
    assert info_emb["first_bad_path"] == (1,)
    assert info_emb["first_violation"]["path"] == (1,)
