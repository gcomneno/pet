# PET local generator rewrite laws

## Scope

This note records bounded observations about local rewrite behavior on canonical PET generators.

It is research-facing only.
Claims below are empirical unless explicitly proved elsewhere.

## Setup

For a canonical PET node with child generators

`g_1 >= g_2 >= ... >= g_k >= 1`

the local constructor is

`Ω(g_1, ..., g_k) = product_i p_i ^ g_i`

with `p_i` the `i`-th prime.

A local rewrite changes one or more child generators while preserving canonical order.

## Bounded results recorded

### 1. Forest aggregation law for disjoint rewrites

For pairwise disjoint rewrites, the resulting root generator is predicted correctly by bottom-up aggregation:

- first aggregate updated child generators at the deepest touched parents
- then propagate those updated parent generators upward
- continue until the root

Bounded checker:
- tool: `tools/forest_rewrite_check.py`
- verified with:
  - `--limit 1000000`
  - `--max-k 3`

Observed summary:
- canonical generators checked: `78`
- checked `k=1`: `252`
- checked `k=2`: `269`
- checked `k=3`: `113`
- mismatches: `0`

Interpretation:
disjoint rewrites behave like a bottom-up forest calculation, not like a naive flat product of independent global effects.

### 2. Prune absorption law

Consider a nested pair where the ancestor rewrite prunes a child by sending its generator to `1`.

Observed behavior:
- descendant then ancestor: valid
- ancestor then descendant: invalid
- descendant then ancestor gives the same result as the ancestor rewrite alone

Bounded checker:
- tool: `tools/prune_absorption_check.py`
- verified with:
  - `--limit 1000000`
  - `--max-pairs 200`

Observed summary:
- canonical generators checked: `78`
- sampled prune pairs: `48`
- descendant then ancestor valid: `48`
- ancestor then descendant invalid: `48`
- absorbed pairs: `48`
- mismatches: `0`

Interpretation:
a pruning rewrite absorbs any rewrite strictly below the pruned branch.

### 3. Admissible nested constructive substitution

For nested constructive rewrites:
- first apply an ancestor rewrite `A`
- then apply a descendant rewrite `B` inside the newly created or enlarged subtree
- let `final_g` be the final generator of that child after `A ; B`

Empirical rule:
`A ; B` behaves like a direct ancestor rewrite replacing that child by `final_g`
only when `final_g` is still admissible among the original siblings of the parent.

So the direct substitution works only under the original local order bounds.

### 4. Order obstruction witness

Small clean obstruction witness observed: `4096`

Local situation:
- root child generators: `[12]`
- at path `(0,)`: parent child generators `[2, 1]`

Constructive nested sequence:
- `A`: at path `(0,)`, slot `1`, rewrite `1 -> 2`
- this creates a new subtree of generator `2`
- `B`: inside that new subtree, rewrite `1 -> 2`
- final generator of that child becomes `4`

But in the original parent `[2, 1]`, slot `1` had upper bound `2`.

So:
- direct substitution would require replacing the second child by `4`
- but `4 > 2`
- therefore the one-step substitution is not canonically admissible in the original parent

Interpretation:
the failure is local and structural.
It is not a mysterious failure of the algebra; it is an order obstruction in the original sibling context.

## Current picture

At this stage the rewrite behavior seems to split into three regimes:

1. disjoint rewrites  
   -> bottom-up forest aggregation

2. nested destructive rewrites  
   -> prune absorption

3. nested constructive rewrites  
   -> direct substitution only when the final child generator remains locally admissible

## Open direction

A useful next step would be to formulate a local theory of rewrite admissibility / obstruction,
instead of searching immediately for a universal substitution law.
