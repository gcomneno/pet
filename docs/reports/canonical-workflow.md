# PET canonical workflow

## Scope

This document defines the current canonical workflow for PET as a bounded,
reproducible structural laboratory for integers.

It does not define PET semantics, proof status, or future theory.
Those belong respectively to `docs/SPEC.md`, `docs/STATUS.md`, and research notes.

## Purpose

The canonical workflow exists to ensure that PET results are produced,
summarized, and interpreted through a stable, explicit pipeline rather than
through scattered ad-hoc exploration.

## Canonical pipeline

### 1. Produce a bounded scan dataset

Primary artifact:
- `docs/reports/data/scan-<start>-<end>.jsonl`

Command pattern:

    python3 -m src.pet.cli scan <start> <end> --jsonl docs/reports/data/scan-<start>-<end>.jsonl

This dataset is the base empirical artifact for downstream reporting.

### 2. Produce an atlas-style summary from the scan dataset

Primary helper:
- `tools/atlas_summary.py`

Derived artifact:
- `docs/reports/data/atlas-summary-<start>-<end>.txt`

Command pattern:

    python3 tools/atlas_summary.py docs/reports/data/scan-<start>-<end>.jsonl > docs/reports/data/atlas-summary-<start>-<end>.txt

This step converts the raw bounded scan into a compact structural summary.

### 3. Publish a bounded report tied to explicit inputs

Primary artifacts:
- `docs/reports/atlas-<start>-<end>.md`
- other bounded report documents under `docs/reports/`

A report is canonical only if it states:
- its bounded range
- the input dataset it depends on
- the command path used to reproduce it
- whether it is descriptive, comparative, or classificatory

### 4. Derive higher-level bounded artifacts from explicit datasets

Current bounded artifact families include:
- atlas reports
- signature catalogs
- family benchmarks
- metrics baselines

These artifacts must stay tied to explicit bounded inputs and must not be
presented as general theory by default.

### 5. Classify statements before promoting them

Interpretation must follow `docs/reports/observation-pipeline.md`.

In practice:
- raw bounded facts belong in reports
- repeated bounded regularities may be called bounded empirical patterns
- beyond-range claims must be marked as conjectures
- proved or definitional statements belong to established status

## Current canonical artifacts

Stable entry points currently recognized by the repository:

- `docs/SPEC.md`
- `docs/STATUS.md`
- `docs/reports/metrics-2-10000.md`
- `docs/reports/atlas-2-100000.md`
- `docs/reports/atlas-2-1000000.md`
- `docs/reports/signatures-catalog-2-1000000.md`
- `docs/reports/families-benchmark-disjoint.md`
- `docs/reports/observation-pipeline.md`

## Current stable vs non-canonical boundary

Canonical workflow does **not** mean every script in `tools/` is stable.

At the current stage, the canonical lab path is centered on:
- bounded scan generation
- atlas-style summarization
- bounded report publication
- explicit statement classification

Exploratory scripts may still be useful, but they are not automatically part of
the canonical workflow unless a report or stable document explicitly relies on them.

## Usage rule

When adding a new PET report, prefer extending the existing bounded pipeline
instead of inventing a parallel undocumented flow.

If a result cannot be reproduced from explicit bounded inputs with a clear command
path, it should not be treated as a canonical PET lab artifact.
