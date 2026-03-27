from __future__ import annotations

import json

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .core import PET


def render(tree: "PET", indent: int = 0) -> str:
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


def to_jsonable(tree: "PET") -> list[dict[str, Any]]:
    return [
        {
            "p": prime,
            "e": None if exp_repr is None else to_jsonable(exp_repr),
        }
        for prime, exp_repr in tree
    ]


def to_json(tree: "PET") -> str:
    return json.dumps(to_jsonable(tree), indent=2, ensure_ascii=False)


def from_jsonable(data: Any) -> "PET":
    from .core import validate

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

        exp_repr = None if exp_data is None else from_jsonable(exp_data)
        tree.append((prime, exp_repr))

    validate(tree)
    return tree


def load_json_file(path: str) -> "PET":
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return from_jsonable(data)
