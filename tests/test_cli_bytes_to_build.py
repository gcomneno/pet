import json
import subprocess
import sys


def _run_cli(*args: str) -> str:
    return subprocess.check_output(
        [sys.executable, "-m", "pet.cli", *args],
        text=True,
    )


def test_cli_bytes_to_build_big_endian_smoke(tmp_path):
    path = tmp_path / "blob.bin"
    path.write_bytes(bytes([0x01, 0x68]))  # 360 big-endian

    out = _run_cli("bytes-to-build", str(path))

    assert f"file = {path}" in out
    assert "byteorder = big" in out
    assert "signed = no" in out
    assert "byte_count = 2" in out
    assert "hex = 0168" in out
    assert "input_n = 360" in out
    assert "factors = 2^3 * 3^2 * 5" in out
    assert "steps = 5" in out
    assert "72 --NEW(p=5)--> 360" in out


def test_cli_bytes_to_build_little_endian_json_smoke(tmp_path):
    path = tmp_path / "blob.bin"
    path.write_bytes(bytes([0xF0, 0x00]))  # 240 little-endian

    out = _run_cli("bytes-to-build", str(path), "--byteorder", "little", "--json")
    payload = json.loads(out)

    assert payload["file"] == str(path)
    assert payload["byteorder"] == "little"
    assert payload["signed"] is False
    assert payload["byte_count"] == 2
    assert payload["hex"] == "f000"
    assert payload["input_n"] == 240
    assert payload["factors"] == [[2, 4], [3, 1], [5, 1]]
    assert payload["target_n"] == 240
    assert payload["steps"] == 5


def test_cli_bytes_to_build_rejects_noncanonical_support(tmp_path):
    path = tmp_path / "blob.bin"
    path.write_bytes(bytes([0x1C]))  # 28

    proc = subprocess.run(
        [sys.executable, "-m", "pet.cli", "bytes-to-build", str(path)],
        text=True,
        capture_output=True,
    )
    assert proc.returncode != 0
    assert "NEW-canonical" in proc.stderr
