# PET tooling classification

## Scope

This document classifies the current `tools/` scripts into stable research
tooling, secondary/non-canonical tooling, and exploratory scripts.

Its goal is to make the PET lab boundary explicit so that workflow documents do
not accidentally treat one-off scripts as stable interfaces.

## Stable research tooling

These scripts are part of the current bounded PET lab workflow and are already
referenced by stable documentation or committed reports.

### `tools/atlas_summary.py`

Status:
- stable research tooling

Reason:
- explicitly used by atlas reports
- explicitly referenced by `README.md`
- explicitly referenced by `docs/reports/canonical-workflow.md`
- consumes bounded scan JSONL input and produces atlas-style summary output

### `tools/cluster_families_disjoint.py`

Status:
- stable research tooling

Reason:
- explicitly used by `docs/reports/families-benchmark-disjoint.md`
- explicitly referenced by `README.md`
- explicitly referenced by `docs/reports/canonical-workflow.md`
- currently defines the canonical family benchmark path

## Secondary / non-canonical research tooling

These scripts are related to documented PET analysis, but are not currently part
of the canonical bounded lab workflow.

### `tools/cluster_families.py`

Status:
- secondary research tooling
- not part of the current canonical workflow

Reason:
- cited in `docs/SPEC.md`
- superseded in the current report workflow by `tools/cluster_families_disjoint.py`
- still meaningful, but not the benchmark path currently promoted by stable lab docs

## Exploratory / one-off tooling

The following scripts are currently exploratory, local, prototype, plotting, or
one-off analysis tools rather than stable workflow interfaces:

- `tools/analyze_generators.py`
- `tools/distinct_shapes.py`
- `tools/distinct_shapes_streamed.py`
- `tools/entropy_growth.py`
- `tools/explore.py`
- `tools/exp_vectors.py`
- `tools/height_distribution.py`
- `tools/omega_distribution.py`
- `tools/pet_compressor_prototipo.py`
- `tools/plot_diagonal_law.py`
- `tools/plot_shape_birth.py`
- `tools/plot_shape_growth_law.py`
- `tools/shape_count_fast.py`
- `tools/shape_entropy.py`
- `tools/shape_evolution_graph.py`
- `tools/shape_first_occurrence.py`
- `tools/shape_graph.py`
- `tools/shapes_growth.py`
- `tools/plot_diagonal_ratio.py`

Common reasons:
- not referenced by the current canonical workflow
- not used directly by committed bounded reports
- rely on hardcoded local paths or local `artifacts/`
- look like prototypes, exploratory utilities, or plotting helpers
- no current stability promise should be inferred from their presence in `tools/`

## Usage rule

Workflow docs, contributor docs, and report regeneration notes should treat only
the current stable research tooling as interface-stable unless this document is
updated.

Exploratory scripts may still be useful for investigation, but they should not
be presented as canonical PET lab commands by default.
