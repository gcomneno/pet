from __future__ import annotations

import argparse
import json
import sys

from .atlas import atlas, draw_shape, extract_shape, print_atlas
from .algebra import distance, structural_distance
from .core import (
    decode,
    encode,
    is_prime,
    metrics_dict,
    minimal_shape_representative,
    prime_factorization,
    shape_generator,
    shape_signature_dict,
    validate,
)
from .io import load_json_file, render, to_json
from .metrics import extended_metrics
from .families import register_subparser as register_families_subparser, run_args as run_families
from .query import register_subparser as register_query_subparser, run_args as run_query
from .metrics import (
    is_expanding,
    is_level_uniform,
    is_linear,
    is_squarefree,
    leaf_ratio,
    profile_shape,
)


def _format_factorization(factors):
    if not factors:
        return "1"

    parts = []
    for prime, exp in factors:
        if exp == 1:
            parts.append(str(prime))
        else:
            parts.append(f"{prime}^{exp}")
    return " * ".join(parts)


def _next_new_prime(support: set[int]) -> int:
    candidate = 2
    while True:
        if candidate not in support and is_prime(candidate):
            return candidate
        candidate += 1


def _explain_moves(n: int) -> dict:
    factors = prime_factorization(n)
    support = {p for p, _ in factors}

    by_exp: dict[int, list[int]] = {}
    for prime, exp in factors:
        by_exp.setdefault(exp, []).append(prime)

    q = _next_new_prime(support)
    new_n = n * q

    moves = {
        "new": {
            "prime": q,
            "target_n": new_n,
            "target_generator": shape_signature_dict(new_n)["generator"],
        },
        "drop": None,
        "inc": [],
        "dec": [],
    }

    for exp in sorted(by_exp):
        primes = sorted(by_exp[exp])
        rep = primes[0]

        inc_n = n * rep
        moves["inc"].append(
            {
                "exponent": exp,
                "count": len(primes),
                "primes": primes,
                "representative_prime": rep,
                "target_n": inc_n,
                "target_generator": shape_signature_dict(inc_n)["generator"],
            }
        )

        if exp >= 2:
            dec_n = n // rep
            moves["dec"].append(
                {
                    "exponent": exp,
                    "count": len(primes),
                    "primes": primes,
                    "representative_prime": rep,
                    "target_n": dec_n,
                    "target_generator": shape_signature_dict(dec_n)["generator"],
                }
            )

    if 1 in by_exp:
        primes = sorted(by_exp[1])
        rep = primes[0]
        drop_n = n // rep
        if drop_n >= 2:
            moves["drop"] = {
                "count": len(primes),
                "primes": primes,
                "representative_prime": rep,
                "target_n": drop_n,
                "target_generator": shape_signature_dict(drop_n)["generator"],
            }

    return moves


def _pathwise_edges_for_number(n: int) -> list[dict]:
    moves = _explain_moves(n)
    edges: list[dict] = []

    new_move = moves["new"]
    edges.append(
        {
            "label": f"NEW(x{new_move['prime']})",
            "target_n": new_move["target_n"],
            "target_generator": new_move["target_generator"],
        }
    )

    drop_move = moves["drop"]
    if drop_move is not None:
        edges.append(
            {
                "label": f"DROP(p={drop_move['representative_prime']})",
                "target_n": drop_move["target_n"],
                "target_generator": drop_move["target_generator"],
            }
        )

    for row in moves["inc"]:
        edges.append(
            {
                "label": f"INC(p={row['representative_prime']},e={row['exponent']})",
                "target_n": row["target_n"],
                "target_generator": row["target_generator"],
            }
        )

    for row in moves["dec"]:
        edges.append(
            {
                "label": f"DEC(p={row['representative_prime']},e={row['exponent']})",
                "target_n": row["target_n"],
                "target_generator": row["target_generator"],
            }
        )

    return edges


def _pathwise_neighborhood(
    n: int,
    depth: int,
    max_nodes: int | None = None,
) -> dict:
    if depth <= 1:
        return {"levels": [], "truncated": False}

    frontier = {n: {"path": []}}
    levels: list[dict] = []
    seen_nodes = {n}
    truncated = False

    for level in range(1, depth + 1):
        next_targets: dict[int, dict] = {}

        for source_n, meta in sorted(frontier.items()):
            source_generator = shape_signature_dict(source_n)["generator"]

            for edge in _pathwise_edges_for_number(source_n):
                target_n = edge["target_n"]
                target_generator = edge["target_generator"]

                if target_n not in seen_nodes:
                    if max_nodes is not None and len(seen_nodes) >= max_nodes:
                        truncated = True
                        continue
                    seen_nodes.add(target_n)

                row = next_targets.setdefault(
                    target_n,
                    {
                        "n": target_n,
                        "generator": target_generator,
                        "from_numbers": set(),
                        "from_generators": set(),
                        "last_step_labels": set(),
                        "path": meta["path"] + [edge["label"]],
                    },
                )
                row["from_numbers"].add(source_n)
                row["from_generators"].add(source_generator)
                row["last_step_labels"].add(edge["label"])

        if not next_targets:
            break

        rows = []
        for target_n in sorted(next_targets):
            row = next_targets[target_n]
            rows.append(
                {
                    "n": row["n"],
                    "generator": row["generator"],
                    "from_numbers": sorted(row["from_numbers"]),
                    "from_generators": sorted(row["from_generators"]),
                    "last_step_labels": sorted(row["last_step_labels"]),
                    "path": row["path"],
                }
            )

        levels.append({"depth": level, "targets": rows})
        frontier = {row["n"]: {"path": row["path"]} for row in rows}

    return {"levels": levels, "truncated": truncated}


def _dot_quote(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\"')


def _pathwise_dot(n: int, depth: int, max_nodes: int | None = None) -> str:
    nodes: dict[int, int] = {n: shape_signature_dict(n)["generator"]}
    edge_labels: dict[tuple[int, int], set[str]] = {}
    frontier = {n}
    seen_nodes = {n}
    truncated = False

    if depth > 1:
        for _level in range(1, depth + 1):
            next_frontier: set[int] = set()

            for source_n in sorted(frontier):
                for edge in _pathwise_edges_for_number(source_n):
                    target_n = edge["target_n"]
                    target_g = edge["target_generator"]
                    label = edge["label"]

                    if target_n not in seen_nodes:
                        if max_nodes is not None and len(seen_nodes) >= max_nodes:
                            truncated = True
                            continue
                        seen_nodes.add(target_n)
                        nodes[target_n] = target_g

                    if target_n in nodes:
                        edge_labels.setdefault((source_n, target_n), set()).add(label)
                        next_frontier.add(target_n)

            if not next_frontier:
                break

            frontier = next_frontier

    lines = [
        "digraph pet_explain {",
        "  rankdir=LR;",
        '  node [shape=box];',
    ]

    if truncated:
        lines.append('  truncated_note [shape=note,label="truncated by --max-nodes"];')

    for node_n in sorted(nodes):
        node_id = f"n_{node_n}"
        node_label = f"N={node_n}\\ng={nodes[node_n]}"
        extra = " style=bold" if node_n == n else ""
        lines.append(f'  {node_id} [label="{_dot_quote(node_label)}"{extra}];')

    for (src, dst) in sorted(edge_labels):
        labels = sorted(edge_labels[(src, dst)])
        edge_label = " / ".join(labels)
        lines.append(
            f'  n_{src} -> n_{dst} [label="{_dot_quote(edge_label)}"];'
        )

    lines.append("}")
    return "\n".join(lines)



def _greedy_dismantle(n: int) -> list[dict]:
    steps: list[dict] = []
    cur = n

    while True:
        factors = prime_factorization(cur)
        cur_g = shape_signature_dict(cur)["generator"]
        cur_fact = _format_factorization(factors)

        if len(factors) == 1 and factors[0][1] == 1:
            steps.append(
                {
                    "n": cur,
                    "factorization": cur_fact,
                    "generator": cur_g,
                    "op": "STOP",
                    "note": "prime reached",
                    "next_n": None,
                    "next_generator": None,
                }
            )
            break

        exp_gt1 = [(exp, prime) for prime, exp in factors if exp >= 2]
        if exp_gt1:
            exp, prime = sorted(exp_gt1, key=lambda item: (-item[0], item[1]))[0]
            nxt = cur // prime
            op = "DEC"
            note = f"prime={prime}, exponent={exp}->{exp - 1}"
        else:
            prime = factors[0][0]
            nxt = cur // prime
            op = "DROP"
            note = f"prime={prime}"

        nxt_g = shape_signature_dict(nxt)["generator"]
        steps.append(
            {
                "n": cur,
                "factorization": cur_fact,
                "generator": cur_g,
                "op": op,
                "note": note,
                "next_n": nxt,
                "next_generator": nxt_g,
            }
        )
        cur = nxt

    return steps


def _explain_data(
    n: int,
    pathwise_depth: int = 1,
    max_nodes: int | None = None,
) -> dict:
    tree = encode(n)
    factors = prime_factorization(n)
    signature = shape_signature_dict(n)
    metrics = metrics_dict(tree)

    return {
        "n": n,
        "pathwise_depth": pathwise_depth,
        "factorization": [{"prime": p, "exponent": e} for p, e in factors],
        "factorization_str": _format_factorization(factors),
        "generator": signature["generator"],
        "already_minimal": signature["already_minimal"],
        "child_generators": signature["child_generators"],
        "signature": signature["signature"],
        "metrics": metrics,
        "moves": _explain_moves(n),
        "max_nodes": max_nodes,
        "pathwise_neighborhood": _pathwise_neighborhood(
            n,
            pathwise_depth,
            max_nodes=max_nodes,
        ),
    }


def _dismantle_data(n: int) -> dict:
    factors = prime_factorization(n)
    signature = shape_signature_dict(n)

    return {
        "n": n,
        "factorization": [{"prime": p, "exponent": e} for p, e in factors],
        "factorization_str": _format_factorization(factors),
        "generator": signature["generator"],
        "steps": _greedy_dismantle(n),
    }



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

    # generator
    p_generator = subparsers.add_parser(
        "generator",
        help="print the smallest integer having the same PET structural shape as N",
    )
    p_generator.add_argument("n", type=int, metavar="N")

    # signature
    p_signature = subparsers.add_parser(
        "signature",
        help="print the canonical structural signature of the PET shape class of N",
    )
    p_signature.add_argument("n", type=int, metavar="N")
    p_signature.add_argument("--json", action="store_true")

    # compare
    p_compare = subparsers.add_parser(
        "compare",
        help="compare two integers via PET distance and structural distance",
    )
    p_compare.add_argument("n1", type=int, metavar="N1")
    p_compare.add_argument("n2", type=int, metavar="N2")
    p_compare.add_argument("--json", action="store_true")

    # classify
    p_classify = subparsers.add_parser(
        "classify",
        help="classify one integer via PET-derived structural predicates",
    )
    p_classify.add_argument("n", type=int, metavar="N")
    p_classify.add_argument("--json", action="store_true")

    # metrics
    p_metrics = subparsers.add_parser("metrics", help="print structural metrics for N")
    p_metrics.add_argument("n", type=int, metavar="N")
    p_metrics.add_argument("--json", action="store_true")

    # extended metrics
    p_xmetrics = subparsers.add_parser(
        "xmetrics",
        help="print extended/research metrics for N",
    )
    p_xmetrics.add_argument("n", type=int, metavar="N")
    p_xmetrics.add_argument("--json", action="store_true")

    # explain
    p_explain = subparsers.add_parser(
        "explain",
        help="explain N as PET building blocks and immediate rewrite moves",
    )
    p_explain.add_argument("n", type=int, metavar="N")
    p_explain.add_argument(
        "--pathwise-depth",
        type=int,
        default=1,
        help="pathwise neighborhood depth (default: 1)",
    )
    p_explain.add_argument(
        "--depth",
        dest="pathwise_depth",
        type=int,
        help=argparse.SUPPRESS,
    )
    p_explain.add_argument(
        "--dot",
        action="store_true",
        help="print the pathwise neighborhood as Graphviz DOT",
    )
    p_explain.add_argument(
        "--max-nodes",
        type=int,
        default=None,
        help="cap the total number of pathwise neighborhood nodes",
    )
    p_explain.add_argument("--json", action="store_true")

    # partial explain
    p_partial_explain = subparsers.add_parser(
        "partial-explain",
        help="run Partial-PET probe + hybrid synthesis and show the top candidate(s)",
    )
    p_partial_explain.add_argument("n", type=int, metavar="N")
    p_partial_explain.add_argument(
        "--schedule",
        default="100,1000,10000",
        help="comma-separated probe schedule, e.g. 10 or 100,1000,10000",
    )
    p_partial_explain.add_argument("--json", action="store_true")

    # preimage search
    p_preimage_search = subparsers.add_parser(
        "preimage-search",
        help="run profiled Partial-PET preimage search from the top ranked seed",
    )
    p_preimage_search.add_argument("n", type=int, metavar="N")
    p_preimage_search.add_argument(
        "--schedule",
        default="10",
        help="comma-separated probe schedule, e.g. 10 or 100,1000,10000",
    )
    p_preimage_search.add_argument(
        "--mode",
        choices=("quick", "deep"),
        default="quick",
        help="search profile mode (default: quick)",
    )
    p_preimage_search.add_argument(
        "--depth",
        type=int,
        default=6,
        help="search depth (default: 6)",
    )
    p_preimage_search.add_argument("--json", action="store_true")

    # dismantle
    p_dismantle = subparsers.add_parser(
        "dismantle",
        help="greedily dismantle N via PET DEC/DROP steps",
    )
    p_dismantle.add_argument("n", type=int, metavar="N")
    p_dismantle.add_argument("--json", action="store_true")

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

    # query / families
    register_query_subparser(subparsers)
    register_families_subparser(subparsers)

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

        elif args.command == "generator":
            print(shape_generator(args.n))

        elif args.command == "signature":
            data = shape_signature_dict(args.n)

            if args.json:
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                print(f"N = {args.n}")
                print(f"generator = {data['generator']}")
                print(f"already_minimal = {data['already_minimal']}")
                print(f"child_generators = {data['child_generators']}")
                print(f"signature = {data['signature']}")

                def _list_to_tuple_shape(obj):
                    if isinstance(obj, list):
                        return tuple(_list_to_tuple_shape(child) for child in obj)
                    return obj

                print("shape:")
                shape = _list_to_tuple_shape(data["signature"])
                lines = draw_shape(shape, lines=[])
                for line in lines:
                    print(line)

        elif args.command == "compare":
            tree1 = encode(args.n1)
            tree2 = encode(args.n2)
            data = {
                "n1": args.n1,
                "n2": args.n2,
                "distance": distance(tree1, tree2),
                "structural_distance": structural_distance(tree1, tree2),
                "same_shape": structural_distance(tree1, tree2) == 0,
            }
            if args.json:
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                print(f"N1 = {args.n1}")
                print(f"N2 = {args.n2}")
                for key, value in data.items():
                    if key in {"n1", "n2"}:
                        continue
                    print(f"{key} = {value}")

        elif args.command == "classify":
            tree = encode(args.n)
            data = {
                "n": args.n,
                "is_linear": is_linear(tree),
                "is_level_uniform": is_level_uniform(tree),
                "is_expanding": is_expanding(tree),
                "is_squarefree": is_squarefree(tree),
                "leaf_ratio": str(leaf_ratio(tree)),
                "profile_shape": profile_shape(tree),
            }
            if args.json:
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                print(f"N = {args.n}")
                for key, value in data.items():
                    if key == "n":
                        continue
                    print(f"{key} = {value}")

        elif args.command == "metrics":
            tree = encode(args.n)
            if args.json:
                print(json.dumps(metrics_dict(tree), indent=2, ensure_ascii=False))
            else:
                print(f"N = {args.n}")
                for key, value in metrics_dict(tree).items():
                    print(f"{key} = {value}")

        elif args.command == "xmetrics":
            tree = encode(args.n)
            data = extended_metrics(tree)
            if args.json:
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                print(f"N = {args.n}")
                for key, value in data.items():
                    print(f"{key} = {value}")

        elif args.command == "explain":
            if args.pathwise_depth < 1:
                raise ValueError("--pathwise-depth must be >= 1")
            if args.max_nodes is not None and args.max_nodes < 1:
                raise ValueError("--max-nodes must be >= 1")
            if args.json and args.dot:
                raise ValueError("--json and --dot cannot be used together")

            data = _explain_data(
                args.n,
                pathwise_depth=args.pathwise_depth,
                max_nodes=args.max_nodes,
            )

            if args.dot:
                print(_pathwise_dot(args.n, args.pathwise_depth, max_nodes=args.max_nodes))
            elif args.json:
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                print(f"N = {data['n']}")
                print(f"factorization = {data['factorization_str']}")
                print(f"generator = {data['generator']}")
                print(f"already_minimal = {data['already_minimal']}")
                print(f"child_generators = {data['child_generators']}")
                print(
                    "metrics =",
                    f"nodes={data['metrics']['node_count']}",
                    f"height={data['metrics']['height']}",
                    f"max_branching={data['metrics']['max_branching']}",
                    f"recursive_mass={data['metrics']['recursive_mass']}",
                )

                print("moves:")
                new_move = data["moves"]["new"]
                print(
                    "  NEW:",
                    f"x{new_move['prime']}",
                    f"-> N'={new_move['target_n']}",
                    f"generator={new_move['target_generator']}",
                )

                drop_move = data["moves"]["drop"]
                if drop_move is None:
                    print("  DROP: unavailable")
                else:
                    print(
                        "  DROP:",
                        f"primes={drop_move['primes']}",
                        f"representative={drop_move['representative_prime']}",
                        f"-> N'={drop_move['target_n']}",
                        f"generator={drop_move['target_generator']}",
                    )

                if data["moves"]["inc"]:
                    print("  INC:")
                    for row in data["moves"]["inc"]:
                        print(
                            "   ",
                            f"e={row['exponent']}",
                            f"primes={row['primes']}",
                            f"representative={row['representative_prime']}",
                            f"-> N'={row['target_n']}",
                            f"generator={row['target_generator']}",
                        )

                if data["moves"]["dec"]:
                    print("  DEC:")
                    for row in data["moves"]["dec"]:
                        print(
                            "   ",
                            f"e={row['exponent']}",
                            f"primes={row['primes']}",
                            f"representative={row['representative_prime']}",
                            f"-> N'={row['target_n']}",
                            f"generator={row['target_generator']}",
                        )
                else:
                    print("  DEC: unavailable")

                neighborhood = data["pathwise_neighborhood"]
                if neighborhood["levels"]:
                    cap = ""
                    if data["max_nodes"] is not None:
                        cap = f", max_nodes={data['max_nodes']}"
                    print(f"pathwise neighborhood (depth={data['pathwise_depth']}{cap}):")
                    for level in neighborhood["levels"]:
                        print(f"  depth {level['depth']}:")
                        for row in level["targets"]:
                            print(
                                "   ",
                                f"n={row['n']}",
                                f"g={row['generator']}",
                                f"from_n={row['from_numbers']}",
                                f"from_g={row['from_generators']}",
                                f"via={row['last_step_labels']}",
                                f"path={' -> '.join(row['path'])}",
                            )
                    if neighborhood["truncated"]:
                        print("  [truncated by --max-nodes]")

        elif args.command == "partial-explain":
            if args.n < 1:
                raise ValueError("N must be >= 1")

            from pathlib import Path

            repo_root = Path(__file__).resolve().parents[2]
            if str(repo_root) not in sys.path:
                sys.path.insert(0, str(repo_root))

            import tools.partial_signature_probe as probe_mod
            from tools.partial_explain import build_partial_explain, render_human

            schedule = probe_mod.parse_schedule(args.schedule)
            data = build_partial_explain(args.n, schedule)

            if args.json:
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                print(render_human(data))

        elif args.command == "preimage-search":
            if args.n < 1:
                raise ValueError("N must be >= 1")
            if args.depth < 1:
                raise ValueError("--depth must be >= 1")

            from pathlib import Path

            repo_root = Path(__file__).resolve().parents[2]
            if str(repo_root) not in sys.path:
                sys.path.insert(0, str(repo_root))

            import tools.partial_signature_probe as probe_mod
            from tools.partial_explain import build_partial_explain
            from tools.pet_preimage_seed import (
                build_seed,
                build_profiled_search_report,
            )

            schedule = probe_mod.parse_schedule(args.schedule)
            partial = build_partial_explain(args.n, schedule)
            seed = build_seed(partial, rank=1)
            report = build_profiled_search_report(seed, depth=args.depth, mode=args.mode)

            if args.json:
                print(json.dumps(report, indent=2, ensure_ascii=False))
            else:
                print(f"N = {report['source_n']}")
                print(f"mode = {report['mode']}")
                print(f"depth = {report['depth']}")
                print(f"profile = {report['profile']}")
                print(f"frontier_count = {report['frontier_count']}")
                print(f"min_n = {report['min_n']}")
                print(f"max_n = {report['max_n']}")
                print(f"sample_ns = {report['sample_ns']}")

        elif args.command == "dismantle":
            data = _dismantle_data(args.n)

            if args.json:
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                print(f"N = {data['n']}")
                print(f"factorization = {data['factorization_str']}")
                print(f"generator = {data['generator']}")
                print("greedy dismantle:")
                for step in data["steps"]:
                    if step["op"] == "STOP":
                        print(
                            "   ",
                            f"STOP at N={step['n']}",
                            f"({step['factorization']})",
                            f"generator={step['generator']}",
                        )
                    else:
                        print(
                            "   ",
                            f"N={step['n']}",
                            f"({step['factorization']})",
                            f"[g={step['generator']}]",
                            f"--{step['op']} {step['note']}-->",
                            f"{step['next_n']}",
                            f"[g={step['next_generator']}]",
                        )

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

        elif args.command == "query":
            return run_query(args)

        elif args.command == "families":
            return run_families(args)

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
