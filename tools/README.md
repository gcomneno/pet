# tools

This directory contains PET research scripts with different stability levels.

Presence in `tools/` does **not** imply that a script is part of the canonical
report-facing workflow or that its interface should be treated as stable.

For the current tooling classification, see
[`../docs/reports/tooling-classification.md`](../docs/reports/tooling-classification.md).

## How to read this directory

- **Stable research tooling**: scripts used by the current bounded,
  report-facing PET lab workflow.
- **Secondary / non-canonical tooling**: useful scripts that are not part of the
  current canonical workflow.
- **Exploratory / one-off tooling**: exploratory, plotting, prototype, or
  historical scripts whose presence here should not be read as a stability
  guarantee.

## Stable research tooling

- `atlas_summary.py` — atlas-style summary generation used by bounded reports
- `cluster_families_disjoint.py` — disjoint family clustering benchmark tooling
  used in the report-facing workflow

## Secondary / non-canonical tooling

- `cluster_families.py` — related family-clustering tooling that is not part of
  the current canonical report-facing path
- `scan_query.py` — small operator-side helper for filtering and grouped counts
  over PET scan JSONL artifacts

## Exploratory / one-off tooling

Unless explicitly classified otherwise in
[`../docs/reports/tooling-classification.md`](../docs/reports/tooling-classification.md),
the remaining scripts in this directory should be treated as exploratory,
plotting-oriented, prototype, or otherwise non-canonical tooling.

## Notes

- Do not infer interface stability from directory placement alone.
- Do not use this README as the source of truth for workflow or artifact policy;
  use the docs under `docs/reports/`.
