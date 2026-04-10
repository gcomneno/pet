from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.partial_signature_probe import build_report
from tools.pet_hybrid_bridge import build_bridge
from tools.pet_hybrid_synthesize import build_candidates


def test_synthesize_filters_candidates_below_root_generator_lower_bound():
    report = build_report(84739348317483740132, [10])
    bridge = build_bridge(report)
    synth = build_candidates(bridge)

    assert bridge["hard_constraints"]["root_generator_lower_bound"] == 420

    assert [c["candidate_kind"] for c in synth["candidates"]] == [
        "minimal-leaf-completion",
        "prime-power-style-completion",
    ]

    assert [c["candidate_root_generator"] for c in synth["candidates"]] == [420, 5040]

    assert all(
        c["candidate_root_generator"] >= bridge["hard_constraints"]["root_generator_lower_bound"]
        for c in synth["candidates"]
    )
