from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.pathwise_first_bad_ancestor_probe import local_ceiling_violations


def test_local_ceiling_violations_empty_on_canonical_list():
    assert local_ceiling_violations([4, 4, 2, 1]) == []


def test_local_ceiling_violations_single_inversion():
    assert local_ceiling_violations([2, 4]) == [
        {"index": 0, "left": 2, "right": 4}
    ]


def test_local_ceiling_violations_multiple_inversions():
    assert local_ceiling_violations([3, 5, 4, 6]) == [
        {"index": 0, "left": 3, "right": 5},
        {"index": 2, "left": 4, "right": 6},
    ]
