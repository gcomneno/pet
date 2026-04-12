import argparse
import json
from pathlib import Path


Shape = tuple

PETRAW_MAGIC = b"PTRW"
PETRAW_VERSION = 0


def normalize_shape(shape: Shape) -> Shape:
    if shape == ():
        return ()
    return tuple(sorted(normalize_shape(child) for child in shape))


def canonical(children) -> Shape:
    return tuple(sorted(children))


def atom(k: int) -> Shape:
    return tuple(() for _ in range(k))


TAG_SEQ_LEAF = atom(14)
TAG_SEQ_PAIR = atom(15)
TAG_LEFT = atom(16)
TAG_RIGHT = atom(17)
SEQ_NIL = atom(18)


def wrap(tag: Shape, payload: Shape) -> Shape:
    return canonical((tag, payload))


def unwrap_tagged(shape: Shape, tag: Shape) -> Shape | None:
    if len(shape) != 2:
        return None
    a, b = shape
    if a == tag:
        return b
    if b == tag:
        return a
    return None


def shape_node_count(shape: Shape) -> int:
    return 1 + sum(shape_node_count(child) for child in shape)


def shape_height(shape: Shape) -> int:
    if shape == ():
        return 0
    return 1 + max(shape_height(child) for child in shape)


def _shape_key(shape: Shape):
    return (shape_node_count(shape), shape)


def _byte_shape_mutations(shape: Shape) -> tuple[Shape, ...]:
    out = set()

    out.add(canonical((shape,)))
    out.add(canonical(shape + ((),)))

    for i, child in enumerate(shape):
        out.add(canonical(shape[:i] + (canonical((child,)),) + shape[i + 1 :]))
        out.add(canonical(shape[:i] + (canonical(child + ((),)),) + shape[i + 1 :]))

    return tuple(sorted(out, key=_shape_key))


def _compact_shape_table(count: int) -> tuple[Shape, ...]:
    ordered: list[Shape] = [()]
    seen: set[Shape] = {()}
    idx = 0

    while len(ordered) < count:
        if idx >= len(ordered):
            raise RuntimeError(f"could not generate {count} distinct compact shapes")

        cur = ordered[idx]
        idx += 1

        for nxt in _byte_shape_mutations(cur):
            if nxt not in seen:
                seen.add(nxt)
                ordered.append(nxt)

        ordered.sort(key=_shape_key)

    return tuple(ordered[:count])


BYTE_TABLE = _compact_shape_table(256)
BYTE_DECODE = {shape: i for i, shape in enumerate(BYTE_TABLE)}


def byte_shape(b: int) -> Shape:
    if not (0 <= b <= 255):
        raise ValueError("byte must be in 0..255")
    return BYTE_TABLE[b]


def decode_byte(shape: Shape) -> int:
    try:
        return BYTE_DECODE[shape]
    except KeyError as exc:
        raise ValueError("invalid byte shape") from exc


def seq_leaf(b: int) -> Shape:
    return canonical((TAG_SEQ_LEAF, byte_shape(b)))


def seq_pair(left: Shape, right: Shape) -> Shape:
    return canonical((
        TAG_SEQ_PAIR,
        wrap(TAG_LEFT, left),
        wrap(TAG_RIGHT, right),
    ))


def encode_bytes(data: bytes) -> Shape:
    def rec(lo: int, hi: int) -> Shape:
        if lo >= hi:
            return SEQ_NIL
        if hi - lo == 1:
            return seq_leaf(data[lo])
        mid = (lo + hi) // 2
        return seq_pair(rec(lo, mid), rec(mid, hi))

    return rec(0, len(data))


def decode_seq(shape: Shape) -> bytes:
    if shape == SEQ_NIL:
        return b""

    if len(shape) == 2:
        payload = unwrap_tagged(shape, TAG_SEQ_LEAF)
        if payload is not None:
            return bytes([decode_byte(payload)])

    if len(shape) == 3:
        saw_pair = False
        left = None
        right = None

        for child in shape:
            if child == TAG_SEQ_PAIR:
                saw_pair = True
                continue

            payload = unwrap_tagged(child, TAG_LEFT)
            if payload is not None:
                if left is not None:
                    raise ValueError("duplicate LEFT branch")
                left = payload
                continue

            payload = unwrap_tagged(child, TAG_RIGHT)
            if payload is not None:
                if right is not None:
                    raise ValueError("duplicate RIGHT branch")
                right = payload
                continue

            raise ValueError("invalid sequence child")

        if saw_pair and left is not None and right is not None:
            return decode_seq(left) + decode_seq(right)

    raise ValueError("invalid encoded sequence shape")


def decode_shape(shape: Shape) -> bytes:
    return decode_seq(shape)


def _uvarint_encode(n: int) -> bytes:
    if n < 0:
        raise ValueError("uvarint requires n >= 0")
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            out.append(b | 0x80)
        else:
            out.append(b)
            return bytes(out)


def _uvarint_decode(data: bytes, pos: int) -> tuple[int, int]:
    shift = 0
    value = 0

    while True:
        if pos >= len(data):
            raise ValueError("truncated uvarint")
        b = data[pos]
        pos += 1
        value |= (b & 0x7F) << shift
        if not (b & 0x80):
            return value, pos
        shift += 7
        if shift > 63:
            raise ValueError("uvarint too large")


def _shape_to_raw_payload(shape: Shape) -> bytes:
    out = bytearray()

    def emit(node: Shape) -> None:
        out.extend(_uvarint_encode(len(node)))
        for child in node:
            emit(child)

    emit(shape)
    return bytes(out)


def _shape_from_raw_payload(data: bytes) -> Shape:
    def parse(pos: int) -> tuple[Shape, int]:
        arity, pos = _uvarint_decode(data, pos)
        children = []
        for _ in range(arity):
            child, pos = parse(pos)
            children.append(child)
        return tuple(children), pos

    shape, pos = parse(0)
    if pos != len(data):
        raise ValueError("trailing bytes after raw PET shape")
    return shape


def shape_to_raw_bytes(shape: Shape) -> bytes:
    payload = _shape_to_raw_payload(shape)
    return PETRAW_MAGIC + bytes([PETRAW_VERSION]) + payload


def shape_from_raw_bytes(data: bytes) -> Shape:
    if len(data) < len(PETRAW_MAGIC) + 1:
        raise ValueError("truncated petraw header")
    if data[:4] != PETRAW_MAGIC:
        raise ValueError("invalid petraw magic")
    version = data[4]
    if version != PETRAW_VERSION:
        raise ValueError(f"unsupported petraw version: {version}")
    payload = data[5:]
    return _shape_from_raw_payload(payload)


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def first_primes(k: int) -> list[int]:
    out: list[int] = []
    cand = 2
    while len(out) < k:
        if is_prime(cand):
            out.append(cand)
        cand += 1
    return out


def shape_witness(shape: Shape) -> int:
    if shape == ():
        return 1

    child_values = []
    for child in shape:
        value = 1 if child == () else shape_witness(child)
        child_values.append((value, child))

    child_values.sort(key=lambda item: item[0], reverse=True)

    n = 1
    for prime, (exp, _child) in zip(first_primes(len(child_values)), child_values):
        n *= prime ** exp
    return n


def to_jsonable(shape: Shape):
    return [to_jsonable(child) for child in shape]


def parse_shape_json(obj) -> Shape:
    if isinstance(obj, dict):
        if "shape" not in obj:
            raise TypeError("shape JSON object must contain a 'shape' field")
        obj = obj["shape"]

    if not isinstance(obj, list):
        raise TypeError("shape JSON must be a nested list or an object with 'shape'")
    return normalize_shape(tuple(parse_shape_json(child) for child in obj))


def _decode_report(shape_path: str, data: bytes) -> dict:
    payload = {
        "shape_json": shape_path,
        "byte_count": len(data),
    }
    if len(data) <= 64:
        payload["bytes_hex"] = data.hex()
    return payload


def cmd_encode(args: argparse.Namespace) -> int:
    data = Path(args.file).read_bytes()
    shape = encode_bytes(data)

    payload = {
        "file": args.file,
        "byte_count": len(data),
        "shape_node_count": shape_node_count(shape),
        "shape_height": shape_height(shape),
        "shape": to_jsonable(shape),
    }

    if args.roundtrip_check:
        payload["roundtrip_ok"] = (decode_shape(shape) == data)

    if args.witness:
        witness = shape_witness(shape)
        payload["witness"] = str(witness)
        payload["witness_digits"] = len(str(witness))

    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def cmd_decode(args: argparse.Namespace) -> int:
    shape = parse_shape_json(json.loads(Path(args.shape_json).read_text(encoding="utf-8")))
    data = decode_shape(shape)

    if args.out:
        Path(args.out).write_bytes(data)

    print(json.dumps(_decode_report(args.shape_json, data), indent=2, ensure_ascii=False))
    return 0


def cmd_encode_raw(args: argparse.Namespace) -> int:
    data = Path(args.file).read_bytes()
    shape = encode_bytes(data)
    raw = shape_to_raw_bytes(shape)
    Path(args.out).write_bytes(raw)

    payload = {
        "file": args.file,
        "raw_out": args.out,
        "byte_count": len(data),
        "petraw_bytes": len(raw),
        "shape_node_count": shape_node_count(shape),
        "shape_height": shape_height(shape),
        "petraw_magic": PETRAW_MAGIC.decode("ascii"),
        "petraw_version": PETRAW_VERSION,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def cmd_decode_raw(args: argparse.Namespace) -> int:
    raw = Path(args.raw_shape).read_bytes()
    shape = shape_from_raw_bytes(raw)
    data = decode_shape(shape)

    if args.out:
        Path(args.out).write_bytes(data)

    payload = {
        "raw_shape": args.raw_shape,
        "petraw_bytes": len(raw),
        "byte_count": len(data),
        "petraw_magic": PETRAW_MAGIC.decode("ascii"),
        "petraw_version": PETRAW_VERSION,
    }
    if len(data) <= 64:
        payload["bytes_hex"] = data.hex()
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Encode raw bytes into a PET-native shape without factorization."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_encode = sub.add_parser("encode", help="encode a file into a PET-native shape JSON payload")
    p_encode.add_argument("file")
    p_encode.add_argument("--witness", action="store_true")
    p_encode.add_argument("--roundtrip-check", action="store_true")
    p_encode.set_defaults(func=cmd_encode)

    p_decode = sub.add_parser("decode", help="decode a PET-native byte-shape JSON file")
    p_decode.add_argument("shape_json")
    p_decode.add_argument("--out")
    p_decode.set_defaults(func=cmd_decode)

    p_encode_raw = sub.add_parser("encode-raw", help="encode a file into raw PET shape bytes (petraw-v0)")
    p_encode_raw.add_argument("file")
    p_encode_raw.add_argument("--out", required=True)
    p_encode_raw.set_defaults(func=cmd_encode_raw)

    p_decode_raw = sub.add_parser("decode-raw", help="decode raw PET shape bytes (petraw-v0)")
    p_decode_raw.add_argument("raw_shape")
    p_decode_raw.add_argument("--out")
    p_decode_raw.set_defaults(func=cmd_decode_raw)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
