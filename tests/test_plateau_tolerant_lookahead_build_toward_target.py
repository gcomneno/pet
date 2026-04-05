from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pet.core import encode
from tools.pathwise_first_bad_ancestor_probe import (
    lookahead_pathwise_build_toward_target,
    plateau_tolerant_lookahead_build_toward_target,
)


def test_plateau_tolerant_builder_has_expected_report_shape():
    start = encode(36)
    result = plateau_tolerant_lookahead_build_toward_target(
        start, target=200, step_limit=5, limit=100
    )

    for key in ("start_h", "final_h", "target", "history", "stop_reason"):
        assert key in result


def test_plateau_tolerant_builder_is_never_worse_than_plain_lookahead():
    start = encode(36)
    target = 200

    plain = lookahead_pathwise_build_toward_target(
        start, target=target, step_limit=5, limit=100
    )
    tolerant = plateau_tolerant_lookahead_build_toward_target(
        start, target=target, step_limit=5, limit=100
    )

    assert abs(tolerant["final_h"] - target) <= abs(plain["final_h"] - target)
