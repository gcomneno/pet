import re
import subprocess
import sys


def _run_cli(*args: str) -> str:
    return subprocess.check_output(
        [sys.executable, "-m", "pet.cli", *args],
        text=True,
    )


def _largest_prime_factor(n: int) -> int:
    x = n
    last = None

    while x % 2 == 0:
        last = 2
        x //= 2

    d = 3
    while d * d <= x:
        while x % d == 0:
            last = d
            x //= d
        d += 2

    if x > 1:
        last = x

    assert last is not None
    return last


def _parse_stop_line(out: str) -> tuple[int, int]:
    m = re.search(r"STOP at N=(\d+) \([^)]+\) generator=(\d+)", out)
    assert m is not None, f"STOP line non trovata\n{out}"
    return int(m.group(1)), int(m.group(2))


def test_cli_dismantle_stops_at_largest_prime_factor_with_generator_two():
    for n in range(2, 301):
        out = _run_cli("dismantle", str(n))
        stop_n, generator = _parse_stop_line(out)
        assert stop_n == _largest_prime_factor(n), (
            f"dismantle({n}) ha terminale {stop_n}, atteso {_largest_prime_factor(n)}"
        )
        assert generator == 2, (
            f"dismantle({n}) ha generator {generator}, atteso 2"
        )
