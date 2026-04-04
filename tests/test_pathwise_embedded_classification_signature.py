from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pet.core import encode, validate
from tools.pathwise_one_step_probe import apply_rw
from tools.pathwise_first_bad_ancestor_probe import classify_pathwise_rewrite


def test_embedded_witness_has_expected_classification_signature():
    tree0 = [
        (2, encode(324)),
        (3, encode(36)),
        (5, None),
    ]
    validate(tree0)

    tree1 = apply_rw(tree0, (1, 1), 0, 2)
    validate(tree1)

    info = classify_pathwise_rewrite(tree0, tree1, (1, 1))

    assert info["local_ok"] is True
    assert info["failure_kind"] == "embedded_ancestor"
    assert info["first_bad_path"] == (1,)
    assert info["first_violation"] is not None
    assert info["first_violation"]["path"] == (1,)
