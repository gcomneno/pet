from __future__ import annotations

import argparse
import ast
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from .core import encode, shape_generator, shape_signature_dict
from .io import to_jsonable


ALLOWED_FIELDS = {
    "generator",
    "signature",
    "height",
    "max_branching",
    "node_count",
    "recursive_mass",
    "branch_profile",
    "average_leaf_depth",
    "leaf_depth_variance",
}

WHERE_RE = re.compile(r"^(?P<field>[a-z_]+)(?P<op>>=|<=|=)(?P<value>.+)$")


def load_rows(path: str | Path):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def _is_signature_value(value: Any) -> bool:
    if not isinstance(value, list):
        return False
    return all(_is_signature_value(child) for child in value)


def _freeze_value(value: Any) -> Any:
    if isinstance(value, list):
        return tuple(_freeze_value(child) for child in value)
    return value


def _thaw_value(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_thaw_value(child) for child in value]
    return value


def parse_value(field: str, raw: str) -> Any:
    raw = raw.strip()

    if field == "branch_profile":
        try:
            value = ast.literal_eval(raw)
        except (SyntaxError, ValueError) as exc:
            raise SystemExit(f"Invalid branch_profile value: {raw}") from exc

        if not isinstance(value, list) or not all(isinstance(x, int) for x in value):
            raise SystemExit(f"branch_profile must be a list of ints: {raw}")

        return value

    if field == "signature":
        try:
            value = ast.literal_eval(raw)
        except (SyntaxError, ValueError) as exc:
            raise SystemExit(f"Invalid signature value: {raw}") from exc

        if not _is_signature_value(value):
            raise SystemExit(f"signature must be a nested list shape: {raw}")

        return value

    if field in {"average_leaf_depth", "leaf_depth_variance"}:
        try:
            return float(raw)
        except ValueError as exc:
            raise SystemExit(f"Expected float value for {field}: {raw}") from exc

    try:
        return int(raw)
    except ValueError as exc:
        raise SystemExit(f"Expected integer value for {field}: {raw}") from exc


def parse_where(expr: str):
    match = WHERE_RE.match(expr.strip())
    if not match:
        raise SystemExit(f"Invalid --where expression: {expr}")

    field = match.group("field")
    op = match.group("op")
    raw_value = match.group("value")

    if field not in ALLOWED_FIELDS:
        raise SystemExit(f"Unsupported field in --where: {field}")

    value = parse_value(field, raw_value)

    if field in {"branch_profile", "signature"} and op != "=":
        raise SystemExit(f"{field} only supports '='")

    return field, op, value


def row_value(row: dict, field: str):
    if field in {"generator", "signature"}:
        return row[field]
    return row["metrics"][field]


def matches_all(row: dict, conditions: list[tuple[str, str, Any]]) -> bool:
    for field, op, expected in conditions:
        actual = row_value(row, field)

        if op == "=":
            if actual != expected:
                return False
        elif op == ">=":
            if actual < expected:
                return False
        elif op == "<=":
            if actual > expected:
                return False
        else:
            raise SystemExit(f"Unsupported operator: {op}")

    return True


def _shape_key(shape):
    if shape is None:
        return ()
    return tuple(_shape_key(child) for child in shape)


def _jsonable_shape(tree):
    if tree is None:
        return None

    children = []
    for node in tree:
        children.append(_jsonable_shape(node["e"]))

    return tuple(sorted(children, key=_shape_key))


def cmd_filter(args: argparse.Namespace) -> int:
    conditions = [parse_where(expr) for expr in args.where]
    shown = 0

    for row in load_rows(args.jsonl_path):
        if matches_all(row, conditions):
            print(json.dumps(row, ensure_ascii=False))
            shown += 1
            if args.limit is not None and shown >= args.limit:
                break

    return 0


def cmd_group_count(args: argparse.Namespace) -> int:
    field = args.field
    if field not in ALLOWED_FIELDS:
        raise SystemExit(f"Unsupported field for --field: {field}")

    counter = Counter()

    for row in load_rows(args.jsonl_path):
        value = row_value(row, field)
        key = _freeze_value(value)
        counter[key] += 1

    for key, count in sorted(counter.items(), key=lambda item: (-item[1], item[0])):
        print(f"{_thaw_value(key)}\t{count}")

    return 0


def cmd_same_shape(args: argparse.Namespace) -> int:
    target_shape = _jsonable_shape(to_jsonable(encode(args.n)))
    shown = 0

    for row in load_rows(args.jsonl_path):
        if _jsonable_shape(row["pet"]) == target_shape:
            print(json.dumps(row, ensure_ascii=False))
            shown += 1
            if args.limit is not None and shown >= args.limit:
                break

    return 0


def cmd_same_signature(args: argparse.Namespace) -> int:
    target_signature = shape_signature_dict(args.n)["signature"]
    shown = 0

    for row in load_rows(args.jsonl_path):
        if row["signature"] == target_signature:
            print(json.dumps(row, ensure_ascii=False))
            shown += 1
            if args.limit is not None and shown >= args.limit:
                break

    return 0


def cmd_signature_family(args: argparse.Namespace) -> int:
    target = shape_signature_dict(args.n)
    target_signature = target["signature"]

    values = []
    generator = None
    checked_schema = False

    for row in load_rows(args.jsonl_path):
        if not checked_schema:
            checked_schema = True
            if "signature" not in row or "generator" not in row:
                schema_version = row.get("schema_version")
                raise SystemExit(
                    "Dataset does not contain 'signature'/'generator' fields; "
                    f"found schema_version={schema_version}. "
                    "Regenerate with current pet scan output (schema_version=2)."
                )

        if row["signature"] == target_signature:
            values.append(row["n"])
            if generator is None:
                generator = row["generator"]

    if not values:
        raise SystemExit("No rows found for target signature")

    summary = {
        "target_n": args.n,
        "signature": target_signature,
        "generator": generator,
        "count": len(values),
        "min_n": min(values),
        "max_n": max(values),
        "first_values": values[: args.preview],
    }

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


def cmd_generator_family(args: argparse.Namespace) -> int:
    target_generator = shape_generator(args.n)

    values = []
    signatures = set()
    checked_schema = False

    for row in load_rows(args.jsonl_path):
        if not checked_schema:
            checked_schema = True
            if "generator" not in row:
                schema_version = row.get("schema_version")
                raise SystemExit(
                    "Dataset does not contain 'generator' field; "
                    f"found schema_version={schema_version}. "
                    "Regenerate with current pet scan output (schema_version=2)."
                )

        if row["generator"] == target_generator:
            values.append(row["n"])
            if "signature" in row:
                signatures.add(json.dumps(row["signature"], sort_keys=True))

    if not values:
        raise SystemExit("No rows found for target generator")

    summary = {
        "target_n": args.n,
        "generator": target_generator,
        "count": len(values),
        "min_n": min(values),
        "max_n": max(values),
        "first_values": values[: args.preview],
    }

    if signatures:
        summary["distinct_signatures"] = len(signatures)

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


def _add_query_subcommands(subparsers) -> None:
    p_filter = subparsers.add_parser(
        "filter",
        help="filter scan rows by simple field predicates",
    )
    p_filter.add_argument("jsonl_path", help="Path to scan JSONL file")
    p_filter.add_argument(
        "--where",
        action="append",
        default=[],
        help="Predicate like generator=12, signature=[[[]],[[]]], height=3, max_branching>=3, branch_profile=[3,1,1]",
    )
    p_filter.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of matching rows to print",
    )
    p_filter.set_defaults(func=cmd_filter)

    p_group = subparsers.add_parser(
        "group-count",
        help="count rows grouped by one scan field",
    )
    p_group.add_argument("jsonl_path", help="Path to scan JSONL file")
    p_group.add_argument("--field", required=True, help="Scan field to group by")
    p_group.set_defaults(func=cmd_group_count)

    p_same_shape = subparsers.add_parser(
        "same-shape",
        help="find scan rows having the same PET structural shape as N",
    )
    p_same_shape.add_argument("jsonl_path", help="Path to scan JSONL file")
    p_same_shape.add_argument("n", type=int, metavar="N")
    p_same_shape.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of matching rows to print",
    )
    p_same_shape.set_defaults(func=cmd_same_shape)

    p_same_signature = subparsers.add_parser(
        "same-signature",
        help="find scan rows having the same canonical PET signature as N",
    )
    p_same_signature.add_argument("jsonl_path", help="Path to scan JSONL file")
    p_same_signature.add_argument("n", type=int, metavar="N")
    p_same_signature.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of matching rows to print",
    )
    p_same_signature.set_defaults(func=cmd_same_signature)

    p_signature_family = subparsers.add_parser(
        "signature-family",
        help="summarize the scan family having the same canonical PET signature as N",
    )
    p_signature_family.add_argument("jsonl_path", help="Path to scan JSONL file")
    p_signature_family.add_argument("n", type=int, metavar="N")
    p_signature_family.add_argument(
        "--preview",
        type=int,
        default=10,
        help="How many first matching values to include in the summary",
    )
    p_signature_family.set_defaults(func=cmd_signature_family)

    p_generator_family = subparsers.add_parser(
        "generator-family",
        help="summarize the scan family having the same PET generator as N",
    )
    p_generator_family.add_argument("jsonl_path", help="Path to scan JSONL file")
    p_generator_family.add_argument("n", type=int, metavar="N")
    p_generator_family.add_argument(
        "--preview",
        type=int,
        default=10,
        help="How many first matching values to include in the summary",
    )
    p_generator_family.set_defaults(func=cmd_generator_family)


def register_subparser(subparsers) -> None:
    p_query = subparsers.add_parser(
        "query",
        help="query scan JSONL artifacts by PET-derived fields",
    )
    query_subparsers = p_query.add_subparsers(
        dest="query_command",
        metavar="QUERY_COMMAND",
        required=True,
    )
    _add_query_subcommands(query_subparsers)


def run_args(args: argparse.Namespace) -> int:
    path = Path(args.jsonl_path)
    if not path.exists():
        raise SystemExit(f"File not found: {args.jsonl_path}")
    return args.func(args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Small operator-side query helper for PET scan JSONL artifacts."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    _add_query_subcommands(subparsers)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return run_args(args)
