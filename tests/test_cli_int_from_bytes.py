import json
import subprocess
import sys


def _run_cli(*args: str) -> str:
    return subprocess.check_output(
        [sys.executable, "-m", "pet.cli", *args],
        text=True,
    )


def test_cli_int_from_bytes_big_endian_smoke(tmp_path):
    path = tmp_path / "blob.bin"
    path.write_bytes(bytes([0x01, 0x02, 0x03, 0x04]))

    out = _run_cli("int-from-bytes", str(path))

    assert f"file = {path}" in out
    assert "byteorder = big" in out
    assert "signed = no" in out
    assert "byte_count = 4" in out
    assert "hex = 01020304" in out
    assert "int = 16909060" in out


def test_cli_int_from_bytes_little_endian_json(tmp_path):
    path = tmp_path / "blob.bin"
    path.write_bytes(bytes([0x01, 0x02, 0x03, 0x04]))

    out = _run_cli("int-from-bytes", str(path), "--byteorder", "little", "--json")
    payload = json.loads(out)

    assert payload["file"] == str(path)
    assert payload["byteorder"] == "little"
    assert payload["signed"] is False
    assert payload["byte_count"] == 4
    assert payload["hex"] == "01020304"
    assert payload["int"] == 67305985


def test_cli_int_from_bytes_signed_smoke(tmp_path):
    path = tmp_path / "neg.bin"
    path.write_bytes(bytes([0xFF, 0xFE]))

    out = _run_cli("int-from-bytes", str(path), "--signed")

    assert "byteorder = big" in out
    assert "signed = yes" in out
    assert "byte_count = 2" in out
    assert "hex = fffe" in out
    assert "int = -2" in out
