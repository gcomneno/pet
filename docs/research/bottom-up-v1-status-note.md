# Bottom-up PET builder v1 status

## Scope

This note records the current bounded operational status of the bottom-up PET builder v1.

## What is now in place

The current bounded pipeline is:

- target
- bounded seed-family proposal
- best-seed selection
- builder execution
- compact result summary

Operational pieces now present:

- one-step pathwise classification
- first bad ancestor / first violation extraction
- root vs embedded obstruction classification
- bounded first non-absorbing ancestor law
- one-step target-aware chooser
- two-step chooser
- greedy builder
- two-step lookahead builder
- compact build summary
- builder comparison helper
- bounded seed-family proposal
- automatic wrapper:
  - `auto_build_toward_target(...)`

## Bounded laws now locked in tests

### Pattern A
- local rewrite around the `36 -> 324` family
- same local rewrite can fail at the root or at an embedded ancestor
- failure location is controlled by the first non-absorbing ancestor

### Pattern B
- local rewrite around the `144 -> 1296` / `[4,2] -> [4,4]` family
- overgrowth failure appears at `[4,4] -> [4,16]`
- this reproduces the same pathwise grammar at a larger local scale

## What is operationally usable

The v1 builder is now usable in a bounded, conservative sense:

- it can propose a bounded seed family for a target
- it can compare candidate seeds
- it can run a target-aware builder
- it can return a compact report with final distance and stop reason

## What did not pay off in the current bounded checks

The plateau-tolerant lookahead builder did not outperform the plain lookahead builder
in the current small controlled benchmark.
So it remains implemented, but is not currently justified as a stronger default.

## Current practical reading

Bottom-up v1 should be treated as:

- bounded
- conservative
- operationally usable
- not yet a general constructive theory for arbitrary large targets

## Recommended next frontier

Do not keep polishing bottom-up v1.

The next honest frontier is either:

1. a poor-but-honest top-down prototype, or
2. a second-generation seed strategy

