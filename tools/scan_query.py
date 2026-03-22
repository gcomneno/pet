#!/usr/bin/env python3
"""Small operator-side query helper for PET scan JSONL artifacts."""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ALLOWED_FIELDS = {
    "height",
    "max_branching",
    "node_count",
    "recursive_mass",
    "branch_profile",
    "average_leaf_depth",
    "leaf_depth_variance",
}

WHERE_RE = re.compile(r"^(?P<field>[a-z_]+)(?P<op>>=|<=|=)(?P<value>.+)$")


def load_rows(path: str):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


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

    if field == "branch_profile" and op != "=":
        raise SystemExit("branch_profile only supports '='")

    return field, op, value


def row_value(row: dict, field: str):
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
        key = tuple(value) if isinstance(value, list) else value
        counter[key] += 1

    for key, count in sorted(counter.items(), key=lambda item: (-item[1], item[0])):
        printable = list(key) if isinstance(key, tuple) else key
        print(f"{printable}\t{count}")

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Small operator-side query helper for PET scan JSONL artifacts."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_filter = subparsers.add_parser("filter", help="Filter scan rows by simple metric predicates")
    p_filter.add_argument("jsonl_path", help="Path to scan JSONL file")
    p_filter.add_argument(
        "--where",
        action="append",
        default=[],
        help="Predicate like height=3, max_branching>=3, branch_profile=[3,1,1]",
    )
    p_filter.add_argument("--limit", type=int, default=None, help="Maximum number of matching rows to print")
    p_filter.set_defaults(func=cmd_filter)

    p_group = subparsers.add_parser("group-count", help="Count rows grouped by one metric field")
    p_group.add_argument("jsonl_path", help="Path to scan JSONL file")
    p_group.add_argument("--field", required=True, help="Metric field to group by")
    p_group.set_defaults(func=cmd_group_count)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    path = Path(args.jsonl_path)
    if not path.exists():
        raise SystemExit(f"File not found: {args.jsonl_path}")

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
