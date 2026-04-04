from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pet.core import encode, validate
from tools.pathwise_one_step_probe import apply_rw
from tools.pathwise_first_bad_ancestor_probe import classify_pathwise_rewrite


def test_first_bad_path_matches_first_nonabsorbing_ancestor_in_root_and_embedded_cases():
    # Case 1: standalone 36 -> 324, root does not absorb growth
    tree0 = encode(36)
    tree1 = apply_rw(tree0, (1,), 0, 2)
    info1 = classify_pathwise_rewrite(tree0, tree1, (1,))

    assert info1["first_bad_path"] == ()
    assert info1["failure_kind"] == "root"
    assert info1["first_violation"] == {
        "path": (),
        "index": 0,
        "left": 2,
        "right": 4,
    }

    # Case 2: explicit canonical embedding, root absorbs but embedded parent does not
    emb0 = [
        (2, encode(324)),
        (3, encode(36)),
        (5, None),
    ]
    validate(emb0)

    emb1 = apply_rw(emb0, (1, 1), 0, 2)
    validate(emb1)
    info2 = classify_pathwise_rewrite(emb0, emb1, (1, 1))

    assert info2["first_bad_path"] == (1,)
    assert info2["failure_kind"] == "embedded_ancestor"
    assert info2["first_violation"] == {
        "path": (1,),
        "index": 0,
        "left": 2,
        "right": 4,
    }
