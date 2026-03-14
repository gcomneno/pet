from __future__ import annotations

import json
import sys

from typing import Any, List, Tuple, Union


PETExp = Union[None, "PET"]
PETNode = Tuple[int, PETExp]
PET = List[PETNode]


def is_prime(n: int) -> bool:
    """Return True if n is prime, else False."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False

    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def prime_factorization(n: int) -> List[Tuple[int, int]]:
    """Return the prime factorization of n as a sorted list of (prime, exponent)."""
    if n < 2:
        raise ValueError("n must be >= 2")

    factors: List[Tuple[int, int]] = []
    d = 2
    while d * d <= n:
        if n % d == 0:
            exp = 0
            while n % d == 0:
                n //= d
                exp += 1
            factors.append((d, exp))
        d = 3 if d == 2 else d + 2

    if n > 1:
        factors.append((n, 1))

    return factors


def encode(n: int) -> PET:
    """Encode an integer n >= 2 into its canonical Prime Exponent Tree."""
    if n < 2:
        raise ValueError("n must be >= 2")

    tree: PET = []
    for prime, exp in prime_factorization(n):
        exp_repr: PETExp = None if exp == 1 else encode(exp)
        tree.append((prime, exp_repr))
    return tree


def validate(tree: PET) -> None:
    """Validate that a tree is a canonical PET."""
    if not isinstance(tree, list) or not tree:
        raise TypeError("tree must be a non-empty list")

    last_prime = 1

    for node in tree:
        if not isinstance(node, tuple) or len(node) != 2:
            raise TypeError("each node must be a tuple (prime, exponent_repr)")

        prime, exp_repr = node

        if not isinstance(prime, int):
            raise TypeError("prime must be an int")

        if not is_prime(prime):
            raise ValueError(f"{prime} is not prime")

        if prime <= last_prime:
            raise ValueError("primes must be strictly increasing at each level")

        last_prime = prime

        if exp_repr is None:
            continue

        if not isinstance(exp_repr, list):
            raise TypeError("exponent_repr must be None or another PET")

        validate(exp_repr)


def decode(tree: PET) -> int:
    """Decode a Prime Exponent Tree back into the represented integer."""
    validate(tree)

    result = 1
    for prime, exp_repr in tree:
        exp = 1 if exp_repr is None else decode(exp_repr)
        result *= prime ** exp
    return result


def _node_count(tree: PET) -> int:
    total = 0
    for _, exp_repr in tree:
        total += 1
        if exp_repr is not None:
            total += _node_count(exp_repr)
    return total


def node_count(tree: PET) -> int:
    validate(tree)
    return _node_count(tree)


def _leaf_count(tree: PET) -> int:
    total = 0
    for _, exp_repr in tree:
        if exp_repr is None:
            total += 1
        else:
            total += _leaf_count(exp_repr)
    return total


def leaf_count(tree: PET) -> int:
    validate(tree)
    return _leaf_count(tree)


def _height(tree: PET) -> int:
    child_heights = [
        _height(exp_repr)
        for _, exp_repr in tree
        if exp_repr is not None
    ]
    if not child_heights:
        return 1
    return 1 + max(child_heights)


def height(tree: PET) -> int:
    validate(tree)
    return _height(tree)


def _max_branching(tree: PET) -> int:
    current = len(tree)
    child_values = [
        _max_branching(exp_repr)
        for _, exp_repr in tree
        if exp_repr is not None
    ]
    if not child_values:
        return current
    return max(current, max(child_values))


def _branch_profile(tree: PET, depth: int, counts: list[int]) -> None:
    if depth == len(counts):
        counts.append(0)

    counts[depth] += len(tree)

    for _, exp_repr in tree:
        if exp_repr is not None:
            _branch_profile(exp_repr, depth + 1, counts)


def branch_profile(tree: PET) -> list[int]:
    validate(tree)
    counts: list[int] = []
    _branch_profile(tree, 0, counts)
    return counts


def max_branching(tree: PET) -> int:
    validate(tree)
    return _max_branching(tree)


def recursive_mass(tree: PET) -> int:
    validate(tree)
    return node_count(tree) - len(tree)


def metrics_dict(tree: PET) -> dict[str, Any]:
    validate(tree)
    return {
        "node_count": node_count(tree),
        "leaf_count": leaf_count(tree),
        "height": height(tree),
        "max_branching": max_branching(tree),
        "branch_profile": branch_profile(tree),
        "recursive_mass": recursive_mass(tree),
    }


def render(tree: PET, indent: int = 0) -> str:
    pad = " " * indent
    lines = [pad + "["]

    for i, (prime, exp_repr) in enumerate(tree):
        is_last = i == len(tree) - 1

        if exp_repr is None:
            line = pad + f"  ({prime}, •)"
            if not is_last:
                line += ","
            lines.append(line)
        else:
            lines.append(pad + f"  ({prime},")
            subtree = render(exp_repr, indent + 4)
            lines.append(subtree)
            closing = pad + "  )"
            if not is_last:
                closing += ","
            lines.append(closing)

    lines.append(pad + "]")
    return "\n".join(lines)


def to_jsonable(tree: PET) -> list[dict[str, Any]]:
    return [
        {
            "p": prime,
            "e": None if exp_repr is None else to_jsonable(exp_repr),
        }
        for prime, exp_repr in tree
    ]


def to_json(tree: PET) -> str:
    return json.dumps(to_jsonable(tree), indent=2, ensure_ascii=False)


def from_jsonable(data: Any) -> PET:
    if not isinstance(data, list) or not data:
        raise TypeError("JSON PET must be a non-empty list")

    tree: PET = []

    for item in data:
        if not isinstance(item, dict):
            raise TypeError("each JSON PET node must be an object")

        if set(item.keys()) != {"p", "e"}:
            raise ValueError("each JSON PET node must contain exactly 'p' and 'e'")

        prime = item["p"]
        exp_data = item["e"]

        if not isinstance(prime, int):
            raise TypeError("'p' must be an integer")

        exp_repr: PETExp
        if exp_data is None:
            exp_repr = None
        else:
            exp_repr = from_jsonable(exp_data)

        tree.append((prime, exp_repr))

    validate(tree)
    return tree


def load_json_file(path: str) -> PET:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return from_jsonable(data)


def main(argv: list[str]) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        prog="pet",
        description="PET — Prime Exponent Tree encoder/decoder",
    )

    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")

    # encode
    p_encode = subparsers.add_parser("encode", help="encode N into PET and print JSON")
    p_encode.add_argument("n", type=int, metavar="N")
    p_encode.add_argument("--json", action="store_true")

    # decode
    p_decode = subparsers.add_parser("decode", help="decode a PET JSON file back to N")
    p_decode.add_argument("file", metavar="FILE.json")

    # render
    p_render = subparsers.add_parser("render", help="render a PET JSON file as tree")
    p_render.add_argument("file", metavar="FILE.json")

    # validate
    p_validate = subparsers.add_parser("validate", help="validate a PET JSON file")
    p_validate.add_argument("file", metavar="FILE.json")

    # metrics
    p_metrics = subparsers.add_parser("metrics", help="print structural metrics for N")
    p_metrics.add_argument("n", type=int, metavar="N")
    p_metrics.add_argument("--json", action="store_true")

    # scan
    p_scan = subparsers.add_parser("scan", help="scan range and output JSONL dataset")
    p_scan.add_argument("start", type=int)
    p_scan.add_argument("end", type=int)
    p_scan.add_argument("--jsonl", required=True)

    # atlas
    p_atlas = subparsers.add_parser(
        "atlas",
        help="compute atlas statistics for a PET dataset",
    )
    p_atlas.add_argument("file", metavar="DATASET.jsonl")

    # shape growth
    p_growth = subparsers.add_parser(
        "shapes-growth",
        help="compute growth of PET structural shapes",
    )
    p_growth.add_argument("file", metavar="DATASET.jsonl")
    p_growth.add_argument("--step", type=int, default=10000)

    # shape generators
    p_generators = subparsers.add_parser(
        "shape-generators",
        help="print the first integer generating each PET structural shape",
    )
    p_generators.add_argument("file", metavar="DATASET.jsonl")
    p_generators.add_argument("--metrics", action="store_true")

    args = parser.parse_args(argv[1:])

    try:
        if args.command == "encode":
            tree = encode(args.n)
            if args.json:
                print(to_json(tree))
            else:
                back = decode(tree)
                print(f"N = {args.n}")
                print(to_json(tree))
                print(f"decoded = {back}")

        elif args.command == "decode":
            tree = load_json_file(args.file)
            print(decode(tree))

        elif args.command == "render":
            tree = load_json_file(args.file)
            print(render(tree))

        elif args.command == "validate":
            tree = load_json_file(args.file)
            validate(tree)
            print("OK")

        elif args.command == "metrics":
            tree = encode(args.n)
            if args.json:
                print(json.dumps(metrics_dict(tree), indent=2, ensure_ascii=False))
            else:
                print(f"N = {args.n}")
                for key, value in metrics_dict(tree).items():
                    print(f"{key} = {value}")

        elif args.command == "scan":
            if args.start < 2:
                raise ValueError("start must be >= 2")

            if args.end < args.start:
                raise ValueError("end must be >= start")

            from .scan import scan_range, write_jsonl
            records = scan_range(args.start, args.end)
            write_jsonl(records, args.jsonl)

        elif args.command == "atlas":
            from .atlas import atlas, print_atlas
            stats = atlas(args.file)
            print_atlas(stats)

        elif args.command == "shapes-growth":
            from .shapes_growth import shapes_growth, print_growth, save_growth

            data = shapes_growth(args.file, args.step)

            print_growth(data)
            save_growth(data)

        elif args.command == "shape-generators":
            import json
            from .atlas import extract_shape, draw_shape

            seen = set()
            index = 0
            generators = []

            with open(args.file, "r", encoding="utf-8") as f:
                for line in f:
                    rec = json.loads(line)

                    n = rec["n"]
                    tree = rec["pet"]
                    metrics = rec["metrics"]

                    shape = extract_shape(tree)

                    if shape not in seen:
                        seen.add(shape)
                        index += 1
                        generators.append(n)

                        print()
                        print(f"shape {index}")
                        print(f"generator: {n}")

                        if args.metrics:
                            print(
                                "metrics:",
                                f"nodes={metrics['node_count']}",
                                f"height={metrics['height']}",
                                f"max_branching={metrics['max_branching']}",
                                f"recursive_mass={metrics['recursive_mass']}",
                            )

                        lines = draw_shape(shape, lines=[])

                        for line in lines:
                            print(line)

            print()
            print("generator sequence G(k):")
            print(generators)

        else:
            parser.print_help()
            return 1

        return 0

    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


def cli() -> None:
    raise SystemExit(main(sys.argv))


if __name__ == "__main__":
    cli()
