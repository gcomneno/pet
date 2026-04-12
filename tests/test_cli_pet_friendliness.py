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
    assert "relaxed_hull_support = (2, 3, 5)" in out
    assert "relaxed_hull_factors = 2^3 * 3^2 * 5" in out
    assert "relaxed_hull_n = 360" in out
    assert "relaxed_hull_build_cost = 5" in out
    assert "relaxed_exact_extra_drop_lower_bound = 0" in out
    assert "relaxed_exact_cost_lower_bound = 5" in out


def test_cli_pet_friendliness_noncanonical_smoke():
    out = _run_cli("pet-friendliness", "28")

    assert "N = 28" in out
    assert "factors = 2^2 * 7" in out
    assert "support = (2, 7)" in out
    assert "strict_pet_friendly = no" in out
    assert "missing_prime_count = 2" in out
    assert "missing_primes_before_max = (3, 5)" in out
    assert "canonical_build_cost = none" in out
    assert "relaxed_hull_support = (2, 3, 5, 7)" in out
    assert "relaxed_hull_factors = 2^2 * 3 * 5 * 7" in out
    assert "relaxed_hull_n = 420" in out
    assert "relaxed_hull_build_cost = 4" in out
    assert "relaxed_exact_extra_drop_lower_bound = 2" in out
    assert "relaxed_exact_cost_lower_bound = 6" in out


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
    assert payload["relaxed_hull_support"] == [2, 3, 5, 7, 11]
    assert payload["relaxed_hull_factors"] == [[2, 1], [3, 1], [5, 1], [7, 1], [11, 1]]
    assert payload["relaxed_hull_n"] == 2310
    assert payload["relaxed_hull_build_cost"] == 4
    assert payload["relaxed_exact_extra_drop_lower_bound"] == 4
    assert payload["relaxed_exact_cost_lower_bound"] == 8
