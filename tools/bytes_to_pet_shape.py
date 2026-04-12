import argparse
import json
from pathlib import Path


Shape = tuple


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
    if not isinstance(obj, list):
        raise TypeError("shape JSON must be a nested list")
    return normalize_shape(tuple(parse_shape_json(child) for child in obj))


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

    payload = {
        "shape_json": args.shape_json,
        "byte_count": len(data),
        "bytes_hex": data.hex(),
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Encode raw bytes into a PET-native shape without factorization."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_encode = sub.add_parser("encode", help="encode a file into a PET-native shape")
    p_encode.add_argument("file")
    p_encode.add_argument("--witness", action="store_true")
    p_encode.add_argument("--roundtrip-check", action="store_true")
    p_encode.set_defaults(func=cmd_encode)

    p_decode = sub.add_parser("decode", help="decode a PET-native byte-shape JSON file")
    p_decode.add_argument("shape_json")
    p_decode.add_argument("--out")
    p_decode.set_defaults(func=cmd_decode)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
