import json
import re
import subprocess
import sys


SUPPORT = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
CASES = [
    (64, 173, 182),
    (128, 386, 395),
    (256, 811, 820),
]


def _run_cli(*args: str) -> str:
    return subprocess.check_output(
        [sys.executable, "-m", "pet.cli", *args],
        text=True,
    )


def _grab(pattern: str, text: str) -> str:
    m = re.search(pattern, text, re.M)
    if not m:
        raise AssertionError(f"pattern not found: {pattern!r}")
    return m.group(1)


def _n_for_e2(e2: int) -> int:
    n = 1
    for p in SUPPORT:
        exp = e2 if p == 2 else 1
        n *= p ** exp
    return n


def test_build_from_factors_large_new_canonical_targets_match_exact_cost(tmp_path):
    for digits, e2, expected_steps in CASES:
        n = _n_for_e2(e2)
        assert len(str(n)) == digits

        payload = {
            "factors": [[p, e2 if p == 2 else 1] for p in SUPPORT]
        }
        factors_path = tmp_path / f"build-{digits}.json"
        factors_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

        build_out = _run_cli("build-from-factors", str(factors_path))
        friendly_out = _run_cli("pet-friendliness", str(n))

        steps = int(_grab(r"^steps = (\d+)$", build_out))
        cost = int(_grab(r"^canonical_build_cost = (\d+)$", friendly_out))
        strict = _grab(r"^strict_pet_friendly = (yes|no)$", friendly_out)

        assert strict == "yes"
        assert steps == cost == expected_steps
        assert f"target_n = {n}" in build_out
        assert " --NEW(p=31)--> " in build_out
