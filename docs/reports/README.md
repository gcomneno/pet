# PET reports and datasets index

This directory is the single source of truth for PET bounded reports, their
associated datasets, and their regeneration paths.

For the canonical end-to-end lab path, see:
- `docs/reports/canonical-workflow.md`

> [!WARNING]
> Some committed scan artifacts under `docs/reports/data/` currently use legacy
> dataset layouts even when their filenames suggest newer scan generations
> (for example `scan-2-*`).
>
> In particular, some existing artifacts do **not** contain current schema-2
> fields such as `generator` and `signature`, and one legacy artifact may even
> lack `schema_version`.
>
> Treat the committed dataset contents as the source of truth, not the filename
> alone. When a workflow requires `generator`/`signature` query support,
> regenerate the dataset with the current `pet scan` command.

## Directory structure

- `docs/reports/` — committed bounded reports and workflow notes
- `docs/reports/data/` — local generated datasets and local derived summary artifacts used to reproduce bounded reports under the current policy

## Report index

### `metrics-2-10000.md`

- purpose: first reproducible bounded PET metrics baseline
- epistemic class: descriptive report
- bounded scope: `2..10000`
- associated dataset: `docs/reports/data/scan-2-10000.jsonl`
- associated summary/tooling: direct scan output
- regeneration command:

      python3 -m src.pet.cli scan 2 10000 --jsonl docs/reports/data/scan-2-10000.jsonl

### `atlas-2-100000.md`

- purpose: bounded empirical atlas snapshot for a medium scan range
- epistemic class: descriptive atlas report
- bounded scope: `2..100000`
- associated dataset: `docs/reports/data/scan-2-100000.jsonl`
- associated summary/tooling: `docs/reports/data/atlas-summary-2-100000.txt`, `tools/atlas_summary.py`
- regeneration commands:

      python3 -m src.pet.cli scan 2 100000 --jsonl docs/reports/data/scan-2-100000.jsonl
      python3 tools/atlas_summary.py docs/reports/data/scan-2-100000.jsonl > docs/reports/data/atlas-summary-2-100000.txt

### `atlas-2-1000000.md`

- purpose: bounded empirical atlas snapshot for a larger scan range
- epistemic class: descriptive atlas report
- bounded scope: `2..1000000`
- associated dataset: `docs/reports/data/scan-2-1000000.jsonl`
- associated summary/tooling: `docs/reports/data/atlas-summary-2-1000000.txt`, `tools/atlas_summary.py`
- regeneration commands:

      python3 -m src.pet.cli scan 2 1000000 --jsonl docs/reports/data/scan-2-1000000.jsonl
      python3 tools/atlas_summary.py docs/reports/data/scan-2-1000000.jsonl > docs/reports/data/atlas-summary-2-1000000.txt

### `signatures-catalog-2-1000000.md`

- purpose: first bounded catalog of PET structural signature components and minimal realizers
- epistemic class: descriptive catalog
- bounded scope: based on the `2..1000000` scan range
- associated dataset: `docs/reports/data/scan-2-1000000.jsonl`
- associated summary/tooling: atlas reports and bounded first-occurrence data from the `2..1000000` scan
- regeneration inputs:
  - `docs/reports/data/scan-2-1000000.jsonl`
  - `docs/reports/atlas-2-1000000.md`

### `families-benchmark-disjoint.md`

- purpose: bounded comparative benchmark across disjoint classical integer families
- epistemic class: benchmark report
- bounded scope: fixed bounded family samples embedded in the benchmark script
- associated dataset: none committed as a separate scan dataset
- associated summary/tooling: `tools/cluster_families_disjoint.py`
- regeneration command:

      python3 tools/cluster_families_disjoint.py

### `observation-pipeline.md`

- purpose: define the vocabulary and promotion rules for PET statements
- epistemic class: pipeline note
- bounded scope: not a dataset report; applies to interpretation across bounded reports
- associated dataset: none
- associated summary/tooling: none

### `canonical-workflow.md`

- purpose: define the canonical PET lab path from bounded inputs to published reports
- epistemic class: workflow note
- bounded scope: current lab process, not a single scan range
- associated dataset: references scan datasets and derived report artifacts
- associated summary/tooling: `tools/atlas_summary.py`, `tools/cluster_families_disjoint.py`

## Local dataset and derived artifact index

### Local generated scan datasets

- `docs/reports/data/scan-2-10000.jsonl` — source dataset for `metrics-2-10000.md`
- `docs/reports/data/scan-2-100000.jsonl` — source dataset for `atlas-2-100000.md`
- `docs/reports/data/scan-2-1000000.jsonl` — source dataset for `atlas-2-1000000.md` and `signatures-catalog-2-1000000.md`

#### Legacy layout note for committed scan datasets

The following committed scan artifacts currently have legacy on-disk layouts,
regardless of the `scan-2-*` filename pattern:

- `docs/reports/data/scan-2-5000.jsonl` — legacy content, actual `schema_version = 1`
- `docs/reports/data/scan-2-10000.jsonl` — legacy content, actual `schema_version = 1`
- `docs/reports/data/scan-2-100000.jsonl` — legacy content, actual `schema_version = 1`
- `docs/reports/data/scan-2-200000.jsonl` — legacy content, actual `schema_version = 1`
- `docs/reports/data/scan-2-1000000.jsonl` — legacy content, no committed `schema_version`, no `generator` / `signature`

These files remain useful as bounded historical artifacts, but workflows that
require current schema-2 fields should regenerate them with the current
`pet scan` command rather than relying on the filename alone.

### Local derived atlas summaries

- `docs/reports/data/atlas-summary-2-100000.txt` — derived summary for `atlas-2-100000.md`
- `docs/reports/data/atlas-summary-2-1000000.txt` — derived summary for `atlas-2-1000000.md`

## Usage rule

When adding a new bounded PET report, update this index so that the report
directory remains navigable as a lab notebook rather than a loose collection of files.
