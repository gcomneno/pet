import json
import subprocess
import sys


def _run(*args: str) -> str:
    return subprocess.check_output(
        [sys.executable, "tools/bytes_to_pet_shape.py", *args],
        text=True,
    )


def test_encode_empty_roundtrip(tmp_path):
    src = tmp_path / "empty.bin"
    src.write_bytes(b"")

    payload = json.loads(_run("encode", str(src), "--roundtrip-check"))
    assert payload["byte_count"] == 0
    assert payload["roundtrip_ok"] is True


def test_encode_ab_roundtrip_without_witness(tmp_path):
    src = tmp_path / "ab.bin"
    src.write_bytes(b"AB")

    payload = json.loads(_run("encode", str(src), "--roundtrip-check"))
    assert payload["byte_count"] == 2
    assert payload["roundtrip_ok"] is True
    assert payload["shape_height"] >= 1
    assert payload["shape_node_count"] >= 1


def test_sequence_order_is_preserved(tmp_path):
    a = tmp_path / "ab.bin"
    b = tmp_path / "ba.bin"
    a.write_bytes(b"AB")
    b.write_bytes(b"BA")

    pa = json.loads(_run("encode", str(a)))
    pb = json.loads(_run("encode", str(b)))

    assert pa["shape"] != pb["shape"]


def test_decode_from_saved_shape_json(tmp_path):
    src = tmp_path / "msg.bin"
    src.write_bytes(b"ciao")

    encoded = json.loads(_run("encode", str(src)))
    shape_path = tmp_path / "shape.json"
    shape_path.write_text(json.dumps(encoded["shape"], indent=2), encoding="utf-8")

    out_path = tmp_path / "out.bin"
    decoded = json.loads(_run("decode", str(shape_path), "--out", str(out_path)))

    assert decoded["byte_count"] == 4
    assert out_path.read_bytes() == b"ciao"


def test_roundtrip_1024_bytes_smoke(tmp_path):
    src = tmp_path / "seq1024.bin"
    src.write_bytes(bytes([i % 256 for i in range(1024)]))

    payload = json.loads(_run("encode", str(src), "--roundtrip-check"))
    assert payload["byte_count"] == 1024
    assert payload["roundtrip_ok"] is True
    assert payload["shape_height"] < 64
