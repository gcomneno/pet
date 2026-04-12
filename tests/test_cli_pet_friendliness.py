import json
import subprocess
import sys


def _run_cli(*args: str) -> str:
    return subprocess.check_output(
        [sys.executable, "-m", "pet.cli", *args],
        text=True,
    )


def test_cli_pet_friendliness_strict_smoke():
    out = _run_cli("pet-friendliness", "360")

    assert "N = 360" in out
    assert "factors = 2^3 * 3^2 * 5" in out
    assert "support = (2, 3, 5)" in out
    assert "support_size = 3" in out
    assert "max_prime = 5" in out
    assert "strict_pet_friendly = yes" in out
    assert "missing_prime_count = 0" in out
    assert "missing_primes_before_max = ()" in out
    assert "canonical_build_cost = 5" in out


def test_cli_pet_friendliness_noncanonical_smoke():
    out = _run_cli("pet-friendliness", "28")

    assert "N = 28" in out
    assert "factors = 2^2 * 7" in out
    assert "support = (2, 7)" in out
    assert "strict_pet_friendly = no" in out
    assert "missing_prime_count = 2" in out
    assert "missing_primes_before_max = (3, 5)" in out
    assert "canonical_build_cost = none" in out


def test_cli_pet_friendliness_json_smoke():
    out = _run_cli("pet-friendliness", "11", "--json")
    payload = json.loads(out)

    assert payload["n"] == 11
    assert payload["factors"] == [[11, 1]]
    assert payload["support"] == [11]
    assert payload["support_size"] == 1
    assert payload["max_prime"] == 11
    assert payload["strict_pet_friendly"] is False
    assert payload["missing_prime_count"] == 4
    assert payload["missing_primes_before_max"] == [2, 3, 5, 7]
    assert payload["canonical_build_cost"] is None
