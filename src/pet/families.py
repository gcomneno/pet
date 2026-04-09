from __future__ import annotations

import argparse

from .algebra import distance, structural_distance
from .core import encode, prime_factorization


FAMILIES_RAW = {
    "Perfect": [6, 28, 496, 8128],
    "Primorials": [2, 6, 30, 210, 2310, 30030, 510510],
    "Hamming": [
        2, 4, 6, 8, 12, 16, 18, 24, 25, 27, 32, 36, 48, 60, 72,
        96, 100, 120, 125, 128, 144, 150, 180, 192, 216, 225,
        240, 243, 250, 256,
    ],
    "HighlyComposite": [
        2, 4, 6, 12, 24, 36, 48, 60, 120, 180, 240, 360,
        720, 840, 1260, 1680, 2520, 5040, 7560, 10080,
        15120, 20160, 25200, 27720, 45360, 50400, 55440,
        83160, 110880, 166320, 221760, 277200, 332640,
        498960, 554400, 665280, 720720,
    ],
}


def make_disjoint(families_raw):
    assigned = set()
    result = {}
    for name, members in families_raw.items():
        exclusive = [m for m in members if m not in assigned]
        assigned.update(exclusive)
        if exclusive:
            result[name] = exclusive
    return result


FAMILIES = make_disjoint(FAMILIES_RAW)


def is_prime_power_value(n: int) -> bool:
    factors = prime_factorization(n)
    return len(factors) == 1 and factors[0][1] >= 2


def is_semiprime_value(n: int) -> bool:
    factors = prime_factorization(n)
    return sum(exp for _, exp in factors) == 2


def is_squarefree_composite_value(n: int) -> bool:
    factors = prime_factorization(n)
    return len(factors) >= 2 and all(exp == 1 for _, exp in factors)


def build_experiment_2_families_raw(start: int, end: int) -> dict[str, list[int]]:
    if start < 2:
        raise ValueError("start must be >= 2")
    if end < start:
        raise ValueError("end must be >= start")

    values = range(start, end + 1)

    return {
        "PrimePowers": [n for n in values if is_prime_power_value(n)],
        "Semiprimes": [n for n in values if is_semiprime_value(n)],
        "Squarefree": [n for n in values if is_squarefree_composite_value(n)],
        "HighlyComposite": [
            n for n in FAMILIES_RAW["HighlyComposite"]
            if start <= n <= end and n >= 4
        ],
    }


def build_experiment_2_families(start: int, end: int) -> dict[str, list[int]]:
    return make_disjoint(build_experiment_2_families_raw(start, end))



def dist_matrix(members, dfunc):
    n = len(members)
    trees = [encode(m) for m in members]
    mat = {}
    for i in range(n):
        for j in range(i + 1, n):
            mat[(i, j)] = dfunc(trees[i], trees[j])
    return mat


def diameter(mat):
    return max(mat.values()) if mat else 0.0


def radius(members, mat):
    n = len(members)
    if n <= 1:
        return 0.0
    eccentricities = []
    for i in range(n):
        ecc = max(
            mat.get((min(i, j), max(i, j)), 0.0)
            for j in range(n)
            if j != i
        )
        eccentricities.append(ecc)
    return min(eccentricities)


def mean_dist(mat):
    vals = list(mat.values())
    return sum(vals) / len(vals) if vals else 0.0


def print_matrix(members, mat, label, width=7):
    n = len(members)
    print(f"\n  Matrice {label} ({n}x{n}):")
    header = " " * 8 + "".join(f"{m:>{width}}" for m in members)
    print(header)
    for i in range(n):
        row = f"  {members[i]:>5}  "
        for j in range(n):
            if i == j:
                row += f"{'0.00':>{width}}"
            else:
                key = (min(i, j), max(i, j))
                row += f"{mat[key]:>{width}.2f}"
        print(row)


def print_matrix_compact(members, mat, label):
    n = len(members)
    print(f"\n  {label} — statistiche per elemento (n={n}):")
    print(f"  {'n':>8}  {'min':>6}  {'mean':>6}  {'max':>6}")
    for i in range(n):
        dists = [
            mat.get((min(i, j), max(i, j)), 0.0)
            for j in range(n)
            if j != i
        ]
        if dists:
            print(
                f"  {members[i]:>8}  {min(dists):>6.2f}  "
                f"{sum(dists) / len(dists):>6.2f}  {max(dists):>6.2f}"
            )


def analyze_family(name, members):
    print(f"\n{'=' * 60}")
    print(f"  {name}  ({len(members)} elementi)")
    print(f"  {members}")
    print(f"{'=' * 60}")

    if len(members) < 2:
        print("  (famiglia singleton — nessuna distanza intra da calcolare)")
        return None, None

    dmat = dist_matrix(members, distance)
    smat = dist_matrix(members, structural_distance)

    compact = len(members) > 12

    if compact:
        print_matrix_compact(members, dmat, "distance")
        print_matrix_compact(members, smat, "structural_distance")
    else:
        print_matrix(members, dmat, "distance")
        print_matrix(members, smat, "structural_distance")

    print("\n  Riassunto:")
    print(
        f"    distance            → diam={diameter(dmat):.2f}  "
        f"rad={radius(members, dmat):.2f}  "
        f"mean={mean_dist(dmat):.2f}"
    )
    print(
        f"    structural_distance → diam={diameter(smat):.2f}  "
        f"rad={radius(members, smat):.2f}  "
        f"mean={mean_dist(smat):.2f}"
    )

    return dmat, smat


def inter_family_distances(families_data, dfunc, label):
    names = list(families_data.keys())
    print(f"\n{'=' * 60}")
    print(f"  Distanze INTER-famiglia — {label}")
    print(f"{'=' * 60}")
    print(
        f"  {'Famiglia A':<20}  {'Famiglia B':<20}  "
        f"{'min':>6}  {'mean':>6}  {'max':>6}"
    )
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            na, nb = names[i], names[j]
            ma = [encode(m) for m in families_data[na]]
            mb = [encode(m) for m in families_data[nb]]
            dists = [dfunc(a, b) for a in ma for b in mb]
            print(
                f"  {na:<20}  {nb:<20}  "
                f"{min(dists):>6.2f}  "
                f"{sum(dists) / len(dists):>6.2f}  "
                f"{max(dists):>6.2f}"
            )


def separability_report(families_data, dfunc, label):
    names = list(families_data.keys())
    print(f"\n  Separabilità ({label}):")
    print(
        f"  {'Coppia':<42}  {'gap_inter_min':>13}  "
        f"{'max_intra':>9}  {'separato?':>9}"
    )

    diams = {}
    for name, members in families_data.items():
        if len(members) < 2:
            diams[name] = 0.0
        else:
            mat = dist_matrix(members, dfunc)
            diams[name] = diameter(mat)

    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            na, nb = names[i], names[j]
            ma = [encode(m) for m in families_data[na]]
            mb = [encode(m) for m in families_data[nb]]
            inter_min = min(dfunc(a, b) for a in ma for b in mb)
            max_intra = max(diams[na], diams[nb])
            sep = "✓ SÌ" if inter_min > max_intra else "✗ NO"
            coppia = f"{na} vs {nb}"
            print(
                f"  {coppia:<42}  {inter_min:>13.2f}  "
                f"{max_intra:>9.2f}  {sep:>9}"
            )


def print_overlap_report(families_raw, families_disjoint):
    print(f"\n{'=' * 60}")
    print("  SOVRAPPOSIZIONI — elementi rimossi per disgiunzione")
    print(f"{'=' * 60}")
    for name, members_orig in families_raw.items():
        kept = set(families_disjoint.get(name, []))
        removed = [m for m in members_orig if m not in kept]
        print(
            f"  {name:<20} orig={len(members_orig):>3}  "
            f"kept={len(kept):>3}  "
            f"removed={removed}"
        )


def run_benchmark(
    families_raw: dict[str, list[int]],
    *,
    title: str,
    priority_line: str,
) -> int:
    families = make_disjoint(families_raw)

    print(title)
    print(priority_line)
    print("distance() e structural_distance()")

    print_overlap_report(families_raw, families)

    for name, members in families.items():
        analyze_family(name, members)

    inter_family_distances(families, distance, "distance")
    inter_family_distances(families, structural_distance, "structural_distance")

    print(f"\n{'=' * 60}")
    print("  SEPARABILITÀ  (gap inter-min > max intra-diam?)")
    print(f"{'=' * 60}")
    separability_report(families, distance, "distance")
    separability_report(families, structural_distance, "structural_distance")

    print(f"\n{'=' * 60}")
    print("  Fine analisi.")
    print(f"{'=' * 60}")
    return 0


def cmd_benchmark_disjoint(args: argparse.Namespace) -> int:
    return run_benchmark(
        FAMILIES_RAW,
        title="PET — Clustering famiglie aritmetiche (DISGIUNTE)",
        priority_line="Priorità: Perfect > Primorials > Hamming > HighlyComposite",
    )


def cmd_benchmark_exp2(args: argparse.Namespace) -> int:
    families_raw = build_experiment_2_families_raw(args.start, args.end)
    return run_benchmark(
        families_raw,
        title="PET — Esperimento 2: famiglie classiche generate su range disgiunto",
        priority_line="Priorità: PrimePowers > Semiprimes > Squarefree > HighlyComposite",
    )


def _add_families_subcommands(subparsers) -> None:
    p_benchmark = subparsers.add_parser(
        "benchmark-disjoint",
        help="run the disjoint classical-family PET benchmark",
    )
    p_benchmark.set_defaults(func=cmd_benchmark_disjoint)

    p_exp2 = subparsers.add_parser(
        "benchmark-exp2",
        help="run experiment 2 on generated disjoint family samples",
    )
    p_exp2.add_argument("--start", type=int, default=2)
    p_exp2.add_argument("--end", type=int, default=200)
    p_exp2.set_defaults(func=cmd_benchmark_exp2)


def register_subparser(subparsers) -> None:
    p_families = subparsers.add_parser(
        "families",
        help="family-level PET benchmarks and comparisons",
    )
    families_subparsers = p_families.add_subparsers(
        dest="families_command",
        metavar="FAMILIES_COMMAND",
        required=True,
    )
    _add_families_subcommands(families_subparsers)


def run_args(args: argparse.Namespace) -> int:
    return args.func(args)
