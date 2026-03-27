from __future__ import annotations

import argparse
import json
import sys

from .atlas import atlas, draw_shape, extract_shape, print_atlas
from .core import decode, encode, metrics_dict, validate
from .io import load_json_file, render, to_json


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv

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
            from .scan import scan_range, write_jsonl

            if args.start < 2:
                raise ValueError("start must be >= 2")

            if args.end < args.start:
                raise ValueError("end must be >= start")

            records = scan_range(args.start, args.end)
            write_jsonl(records, args.jsonl)

        elif args.command == "atlas":
            stats = atlas(args.file)
            print_atlas(stats)

        elif args.command == "shape-generators":
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
    raise SystemExit(main())


if __name__ == "__main__":
    cli()
