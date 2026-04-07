# PET — Prime Exponent Tree

[![CI](https://github.com/gcomneno/pet/actions/workflows/ci.yml/badge.svg)](https://github.com/gcomneno/pet/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/gcomneno/pet)](https://github.com/gcomneno/pet/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)

PET is a Python CLI and research playground for representing integers as recursive prime-exponent trees.

It treats an integer not only as a value, but also as a structured multiplicative object.  
The goal is to make that structure inspectable, measurable, and comparable.

## Why this is interesting

PET gives you a way to explore integers through their recursive prime-factorization structure.

It is useful as:

- a canonical representation of integers based on prime factorization
- a CLI for inspecting structural metrics of integers
- a reproducible lab for scans, queries, summaries, and empirical reports

PET is presented as a structural lens and research playground — not as a claimed solution to a major open problem.

## Try it in 30 seconds

### Install locally

```bash
pip install -e .
```

### Inspect a number

```bash
pet encode 72
```

Output:

```text
N = 72
[
  {
    "p": 2,
    "e": [
      {
        "p": 3,
        "e": null
      }
    ]
  },
  {
    "p": 3,
    "e": [
      {
        "p": 2,
        "e": null
      }
    ]
  }
]
decoded = 72
```

### Inspect structural metrics

```bash
pet metrics 256
```

Output:

```text
N = 256
node_count = 3
leaf_count = 1
height = 3
max_branching = 1
branch_profile = [1, 1, 1]
recursive_mass = 2
average_leaf_depth = 3.0
leaf_depth_variance = 0.0
```

### Run a small bounded scan

```bash
pet scan 2 1000 --jsonl artifacts/scan-2-1000.jsonl
```

### Query the scan

```bash
pet query filter artifacts/scan-2-1000.jsonl --where "height=2" --limit 5
```

## What is stable today

The project already treats some parts as stable and others as exploratory.

Stable/core ideas:

- recursive encoding based on prime factorization
- canonical representation
- invertibility / roundtrip behavior
- machine-facing JSON representation
- CLI-based inspection and dataset generation

Exploratory/research-facing areas:

- structural patterns in large scans
- useful invariants over PET shapes
- classification of integer families through PET metrics
- possible future algebraic layers

For the precise claim-by-claim status, see [docs/STATUS.md](docs/STATUS.md).

## Project map

Start here depending on what you need:

- [docs/CLI.md](docs/CLI.md) — command-line usage
- [docs/SPEC.md](docs/SPEC.md) — format, schema, metrics, and behavior contracts
- [docs/STATUS.md](docs/STATUS.md) — what is defined, proved, empirical, or still open
- [docs/reports/README.md](docs/reports/README.md) — reproducible reports, datasets, and regeneration commands
- [ROADMAP.md](ROADMAP.md) — current priorities and likely next directions
- [CHANGELOG.md](CHANGELOG.md) — public release history

## Typical workflow

A small practical PET workflow looks like this:

1. encode or inspect specific integers
2. generate a bounded JSONL scan
3. query or group the scan
4. summarize the dataset with report tooling
5. compare structural families empirically

## Current scope

PET is currently best understood as:

- a small Python CLI
- a reproducible research/tooling lab
- a project for studying structural properties of integers through PET representations

It is not yet packaged or presented as a polished end-user product.

## Development

The project targets Python 3.10+.

Local install:

```bash
pip install -e .
```

Run tests:

```bash
pytest -q
```

## License

MIT
