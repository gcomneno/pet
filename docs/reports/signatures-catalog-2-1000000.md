# PET structural signatures catalog (2..1000000)

## Scope

This document proposes a compact descriptive vocabulary for PET structural signatures
based on bounded evidence from the scan range `2..1000000`.

It focuses on reusable signature components that already appear in the codebase or
in bounded empirical reports: structural shape, branch profile, profile shape,
height, maximum branching, recursive mass, and minimal realizer.

The goal is descriptive stability, not complete classification.

## Reproduction

### Command

    python3 -m src.pet.cli scan 2 1000000 --jsonl docs/reports/data/scan-2-1000000.jsonl

### Input basis

This catalog is based on bounded evidence from the scan dataset
`docs/reports/data/scan-2-1000000.jsonl`.

It also consolidates stable signature components already reused in current PET
reports and code-facing descriptors.

## Proposed signature vocabulary

A practical PET structural signature can be described by the tuple

`(shape, branch_profile, profile_shape, height, max_branching, recursive_mass)`.

- `shape` is the full prime-free rooted structure.
- `branch_profile` records the number of nodes at each depth level.
- `profile_shape` is a compact morphological classifier (`point`, `linear`, `normal`, `expanding`, `bell`).
- `height`, `max_branching`, and `recursive_mass` provide stable scalar descriptors.
- the minimal realizer of a signature component is the smallest `n` in the bounded scan where that component first appears.

## Representative signatures and minimal realizers

A first compact catalog can start from stable components already observed in bounded scans.

| component | signature value | minimal realizer |
|---|---|---:|
| `profile_shape` | `point` | 2 |
| `profile_shape` | `linear` | 4 |
| `profile_shape` | `normal` | 12 |
| `profile_shape` | `expanding` | 64 |
| `profile_shape` | `bell` | 4096 |
| `recursive_mass` | `0` | 2 |
| `recursive_mass` | `1` | 4 |
| `recursive_mass` | `2` | 16 |
| `recursive_mass` | `3` | 144 |
| `recursive_mass` | `4` | 1296 |
| `recursive_mass` | `5` | 32400 |
| `recursive_mass` | `6` | 810000 |

## Stability notes

The components above are relatively stable because they already have explicit operational meaning in the current codebase and reports.

`branch_profile`, `profile_shape`, `height`, `max_branching`, and `recursive_mass` are usable descriptive components today.
The full `shape` is also stable as a prime-free rooted structure, but its human-facing naming scheme is not yet standardized.

Minimal realizers in this document are bounded empirical minima within `2..1000000`.
They should be treated as reproducible observations, not as proofs of global minimality beyond the scanned range.

## Transition-law note

A further bounded empirical result is that elementary transitions between PET
generator families behave deterministically in the tested range.

Checked setup:
- source values: `2..100000`
- tested primes for local moves: `2, 3, 5, 7, 11, 13, 17, 19, 23, 29`

Observed bounded laws:

### 1. `T_new(g)`

If a number in generator family `g` is multiplied by a **new prime** not already
present in its factorization, the target generator family is determined only by `g`.

Examples:
- `2 -> 6`
- `6 -> 30`
- `30 -> 210`
- `60 -> 420`
- `210 -> 2310`

### 2. `T_inc(g, e)`

If a number in generator family `g` is multiplied by an **existing prime**
already present with exponent `e`, the target generator family is determined
only by `(g, e)`.

Examples:
- `6, e=1 -> 12`
- `30, e=1 -> 60`
- `60, e=2 -> 60`
- `60, e=3 -> 240`
- `60, e=5 -> 960`

### 3. `T_drop(g)`

If a prime factor of exponent `1` is removed, the source generator family `g`
moves to a target family determined only by `g`.

Examples:
- `6 -> 2`
- `30 -> 6`
- `210 -> 30`
- `420 -> 60`
- `2310 -> 210`

### 4. `T_dec(g, e)`

If the exponent of an existing prime is decreased from `e` to `e-1`, the target
generator family is determined only by `(g, e)`.

Examples:
- `12, e=2 -> 6`
- `12, e=3 -> 12`
- `12, e=5 -> 48`
- `60, e=2 -> 30`
- `60, e=3 -> 60`
- `60, e=5 -> 240`

### Bounded determinism status

Observed checks:
- non-deterministic `T_new` classes: `0`
- non-deterministic `T_inc` classes: `0`
- non-deterministic `T_drop` classes: `0`
- non-deterministic `T_dec` classes: `0`

This should currently be treated as a bounded empirical pattern, not as a theorem.


## Observations

1. The catalog does not attempt a full taxonomy of all PET forms; it isolates a
   compact subset of signature components that already have stable descriptive use.

2. `profile_shape`, `height`, `max_branching`, and `recursive_mass` already form
   a practical bounded vocabulary for comparing PET structures across reports.

3. Minimal realizers listed here are bounded empirical first occurrences within
   `2..1000000`, so they are useful as reproducible reference points but not as
   global minimality claims.

## Limits

This catalog is descriptive and bounded.

It does not claim a complete classification of PET forms, a final naming system for all shapes,
or global minimality results beyond the scanned range.
