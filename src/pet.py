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
    """Return the total number of nodes in a valid PET."""
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
    """Return the total number of terminal nodes in a valid PET."""
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
    """Return the recursive height of a valid PET."""
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
    """Return the number of nodes at each recursive PET level."""
    validate(tree)
    counts: list[int] = []
    _branch_profile(tree, 0, counts)
    return counts


def max_branching(tree: PET) -> int:
    """Return the maximum number of nodes at any single PET level."""
    validate(tree)
    return _max_branching(tree)


def render(tree: PET, indent: int = 0) -> str:
    """Render a PET in a readable multiline format with proper commas."""
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
    """Convert a PET into a JSON-serializable structure."""
    return [
        {
            "p": prime,
            "e": None if exp_repr is None else to_jsonable(exp_repr),
        }
        for prime, exp_repr in tree
    ]


def to_json(tree: PET) -> str:
    """Convert a PET into pretty-printed JSON."""
    return json.dumps(to_jsonable(tree), indent=2, ensure_ascii=False)


def from_jsonable(data: Any) -> PET:
    """Convert JSON-loaded data into internal PET representation."""
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
    """Load a PET from a JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return from_jsonable(data)


def print_usage() -> None:
    print("Usage:")
    print("  python3 pet.py NUMBER")
    print("  python3 pet.py --json NUMBER")
    print("  python3 pet.py --metrics NUMBER")
    print("  python3 pet.py --decode FILE.json")
    print("  python3 pet.py --render FILE.json")
    print("  python3 pet.py --validate FILE.json")


def main(argv: list[str]) -> int:
    try:
        if len(argv) == 2:
            n = int(argv[1])
            tree = encode(n)
            back = decode(tree)
            print(f"N = {n}")
            print(to_json(tree))
            print(f"decoded = {back}")
            return 0

        if len(argv) == 3 and argv[1] == "--json":
            n = int(argv[2])
            tree = encode(n)
            print(to_json(tree))
            return 0

        if len(argv) == 3 and argv[1] == "--metrics":
            n = int(argv[2])
            tree = encode(n)
            print(f"N = {n}")
            print(f"node_count = {node_count(tree)}")
            print(f"leaf_count = {leaf_count(tree)}")
            print(f"height = {height(tree)}")
            print(f"max_branching = {max_branching(tree)}")
            print(f"branch_profile = {branch_profile(tree)}")
            return 0

        if len(argv) == 3 and argv[1] == "--decode":
            tree = load_json_file(argv[2])
            print(decode(tree))
            return 0

        if len(argv) == 3 and argv[1] == "--render":
            tree = load_json_file(argv[2])
            print(render(tree))
            return 0

        if len(argv) == 3 and argv[1] == "--validate":
            tree = load_json_file(argv[2])
            validate(tree)
            print("OK")
            return 0

        print_usage()
        return 1

    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
