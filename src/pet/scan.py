import json
import sys

from .core import encode, metrics_dict
from .io import to_jsonable


def build_record(n: int) -> dict:
    tree = encode(n)

    return {
        "schema_version": 1,
        "n": n,
        "pet": to_jsonable(tree),
        "metrics": metrics_dict(tree),
        "meta": {
            "pet_format": "canonical-json",
        },
    }


def scan_range(start: int, end: int):
    for n in range(start, end + 1):
        if n % 10000 == 0:
            print(f"scanned {n}", file=sys.stderr)
        yield build_record(n)


def write_jsonl(records, path):
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, separators=(",", ":"), ensure_ascii=False))
            f.write("\n")
