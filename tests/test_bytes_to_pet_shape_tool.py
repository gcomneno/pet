import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


def _load_tool_module():
    tool_path = Path("tools/bytes_to_pet_shape.py")
    spec = importlib.util.spec_from_file_location("bytes_to_pet_shape_tool", tool_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load tool module from {tool_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_tool = _load_tool_module()
encode_bytes = _tool.encode_bytes
shape_to_raw_bytes = _tool.shape_to_raw_bytes
shape_from_raw_bytes = _tool.shape_from_raw_bytes
PETRAW_MAGIC = _tool.PETRAW_MAGIC
PETRAW_VERSION = _tool.PETRAW_VERSION


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


def test_shape_raw_roundtrip_in_memory():
    shape = encode_bytes(bytes([0, 1, 2, 3, 255]))
    raw = shape_to_raw_bytes(shape)
    got = shape_from_raw_bytes(raw)
    assert got == shape
    assert raw[:4] == PETRAW_MAGIC
    assert raw[4] == PETRAW_VERSION


def test_encode_raw_and_decode_raw_roundtrip(tmp_path):
    src = tmp_path / "msg.bin"
    src.write_bytes(b"Ciao PET\n")

    raw_path = tmp_path / "msg.petraw"
    out_path = tmp_path / "msg.out"

    enc = json.loads(_run("encode-raw", str(src), "--out", str(raw_path)))
    dec = json.loads(_run("decode-raw", str(raw_path), "--out", str(out_path)))

    assert enc["byte_count"] == 9
    assert enc["petraw_bytes"] > 5
    assert enc["petraw_magic"] == "PTRW"
    assert enc["petraw_version"] == 0
    assert dec["byte_count"] == 9
    assert dec["petraw_magic"] == "PTRW"
    assert dec["petraw_version"] == 0
    assert out_path.read_bytes() == b"Ciao PET\n"


def test_decode_accepts_full_payload_object(tmp_path):
    src = tmp_path / "msg.bin"
    src.write_bytes(b"ok")

    payload = json.loads(_run("encode", str(src)))
    payload_path = tmp_path / "payload.json"
    payload_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    out_path = tmp_path / "out.bin"
    decoded = json.loads(_run("decode", str(payload_path), "--out", str(out_path)))

    assert decoded["byte_count"] == 2
    assert out_path.read_bytes() == b"ok"


def test_petraw_rejects_bad_magic():
    shape = encode_bytes(b"abc")
    raw = shape_to_raw_bytes(shape)
    broken = b"XXXX" + raw[4:]

    with pytest.raises(ValueError, match="invalid petraw magic"):
        shape_from_raw_bytes(broken)


def test_petraw_rejects_wrong_version():
    shape = encode_bytes(b"abc")
    raw = shape_to_raw_bytes(shape)
    broken = raw[:4] + bytes([PETRAW_VERSION + 1]) + raw[5:]

    with pytest.raises(ValueError, match="unsupported petraw version"):
        shape_from_raw_bytes(broken)


def test_petraw_rejects_trailing_bytes():
    shape = encode_bytes(b"abc")
    raw = shape_to_raw_bytes(shape) + b"\x00"

    with pytest.raises(ValueError, match="trailing bytes after raw PET shape"):
        shape_from_raw_bytes(raw)


def test_petraw_rejects_truncated_uvarint():
    broken = PETRAW_MAGIC + bytes([PETRAW_VERSION]) + b"\x80"

    with pytest.raises(ValueError, match="truncated uvarint"):
        shape_from_raw_bytes(broken)
