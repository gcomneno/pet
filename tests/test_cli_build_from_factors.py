import json
import subprocess
import sys


def _run_cli(*args: str) -> str:
    return subprocess.check_output(
        [sys.executable, "-m", "pet.cli", *args],
        text=True,
    )


def _write_factor_file(tmp_path, payload):
    path = tmp_path / "factors.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_cli_build_from_factors_smoke(tmp_path):
    path = _write_factor_file(tmp_path, {"factors": [[2, 3], [3, 2], [5, 1]]})
    out = _run_cli("build-from-factors", str(path))

    assert "factors = 2^3 * 3^2 * 5" in out
    assert "target_n = 360" in out
    assert "steps = 5" in out
    assert "2 --INC(p=2,e=1)--> 4" in out
    assert "72 --NEW(p=5)--> 360" in out


def test_cli_build_from_factors_json_smoke(tmp_path):
    path = _write_factor_file(tmp_path, [[2, 4], [3, 1], [5, 1]])
    out = _run_cli("build-from-factors", str(path), "--json")
    payload = json.loads(out)

    assert payload["start_n"] == 2
    assert payload["factors"] == [[2, 4], [3, 1], [5, 1]]
    assert payload["target_n"] == 240
    assert payload["steps"] == 5
    assert payload["path"][0]["source_n"] == 2
    assert payload["path"][-1]["target_n"] == 240


def test_cli_build_from_factors_two_only(tmp_path):
    path = _write_factor_file(tmp_path, {"factors": [[2, 5]]})
    out = _run_cli("build-from-factors", str(path))

    assert "factors = 2^5" in out
    assert "target_n = 32" in out
    assert "steps = 4" in out
    assert "16 --INC(p=2,e=4)--> 32" in out
