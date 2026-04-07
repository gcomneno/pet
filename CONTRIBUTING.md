# Contributing to PET

Thanks for your interest in PET.

This project is currently a small Python CLI and research/tooling lab for exploring recursive prime-exponent-tree representations of integers.

## Before you start

Please prefer:

- small, focused changes
- clear commit messages
- tests for behavior changes
- documentation updates when user-facing behavior changes

When possible, do not mix unrelated work in the same change.
For example, avoid combining a bug fix, a refactor, and a documentation rewrite in one PR.

## Local setup

Create and activate a virtual environment, then install the project in editable mode:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Running tests

Run the test suite with:

```bash
pytest -q
```

You can also use the Makefile test target:

```bash
make test
```

## Useful project entry points

If you are changing behavior or documentation, these files are usually the most relevant:

- `README.md`
- `docs/CLI.md`
- `docs/SPEC.md`
- `docs/STATUS.md`
- `docs/reports/README.md`

Core implementation lives under:

- `src/pet/`

Tests live under:

- `tests/`

## Change guidelines

### CLI and behavior changes

If you change CLI behavior, output shape, or semantics:

- update the relevant CLI documentation
- update or add tests
- keep examples aligned with actual output

### Stable vs exploratory material

PET contains both stable/core material and exploratory/research-facing material.

Please keep that distinction explicit:

- stable definitions, contracts, and behavior belong in the main docs and implementation
- exploratory observations, bounded empirical patterns, and research-facing notes should stay in the appropriate research/report documents

Do not present exploratory observations as established facts.

### Scope discipline

Prefer one kind of change per PR when possible:

- docs
- behavior
- refactor
- tooling

Small, reviewable PRs are strongly preferred over broad mixed changes.

## Style

There is no heavy formal contribution process yet.

For now:

- follow the existing code and doc style
- keep names and output consistent with the rest of the repo
- prefer clarity over cleverness

## Pull requests

A good pull request should make it easy to answer:

- what changed
- why it changed
- how it was validated

Include test or reproduction notes when relevant.

## Issues

Bug reports and focused improvement suggestions are welcome.

When reporting a problem, include:

- the command you ran
- the observed output or traceback
- the expected behavior
- enough context to reproduce the issue
