#!/usr/bin/env python3
import json
import subprocess
import sys


def test_partial_explain_json_prime_residue():
    result = subprocess.run(
        [
            sys.executable,
            "tools/partial_explain.py",
            "8473934831",
            "--schedule",
            "10",
            "--json",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    data = json.loads(result.stdout)

    assert data["n"] == 8473934831
    assert data["schedule"] == [10]

    probe = data["probe"]
    assert probe["stop_reason"] == "closed-prime-residue"
    assert probe["closure_kind"] == "prime-residue"
    assert probe["exact_root_anatomy"] is True
    assert probe["known_root_children"] == []
    assert probe["root_generator_lower_bound"] == 2
    assert probe["exact_root_children"] == [[]]
    assert probe["exact_root_generator"] == 2

    top = data["top_candidate"]
    assert top["candidate_kind"] == "exact-root-anatomy"
    assert top["candidate_root_generator"] == 2
    assert top["candidate_root_children"] == [[]]


def test_partial_explain_json_partial_composite_case():
    result = subprocess.run(
        [
            sys.executable,
            "tools/partial_explain.py",
            "84739348317483740132",
            "--schedule",
            "10",
            "--json",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    data = json.loads(result.stdout)

    assert data["n"] == 84739348317483740132
    assert data["schedule"] == [10]

    probe = data["probe"]
    assert probe["stop_reason"] == "budget-exhausted-composite-unknown"
    assert probe["closure_kind"] is None
    assert probe["exact_root_anatomy"] is False
    assert probe["known_root_children"] == [[], [[]]]
    assert probe["known_root_generator_lower_bound"] == 12
    assert probe["residual_info"]["status"] == "composite-non-prime-power"
    assert probe["root_generator_lower_bound"] == 420

    assert data["candidate_count"] == 3

    top = data["top_candidate"]
    assert top["candidate_kind"] == "minimal-leaf-completion"
    assert top["candidate_root_generator"] == 420
    assert top["candidate_root_children"] == [[], [], [], [[]]]


def test_partial_explain_human_output():
    result = subprocess.run(
        [
            sys.executable,
            "tools/partial_explain.py",
            "84739348317483740132",
            "--schedule",
            "10",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    expected = [
        "N = 84739348317483740132",
        "schedule = [10]",
        "stop_reason = budget-exhausted-composite-unknown",
        "closure_kind = None",
        "exact_root_anatomy = False",
        "known_root_children = [[], [[]]]",
        "known_root_generator_lower_bound = 12",
        "root_generator_lower_bound = 420",
        "residual_status = composite-non-prime-power",
        "residual_digits = 19",
        "candidate_count = 3",
        "",
        "top_candidate:",
        "  rank = 1",
        "  kind = minimal-leaf-completion",
        "  root_generator = 420",
        "  root_children = [[], [], [], [[]]]",
        "",
        "top_candidates:",
        "  [1] kind=minimal-leaf-completion root_generator=420 root_children=[[], [], [], [[]]]",
        "  [2] kind=grouped-leaf-completion root_generator=180 root_children=[[], [[]], [[]]]",
        "  [3] kind=prime-power-style-completion root_generator=5040 root_children=[[], [], [[]], [[[]]]]",
    ]

    assert result.stdout.strip().splitlines() == expected
