# PET multiplicative grammar

## Scope

This note records a small structural grammar for PET in the **multiplicative domain**.

It does **not** solve exact PET computation for large integers without factorization.
It does **not** provide a general rule for additive exponent collision (`e1 + e2`).

What it does provide is a compact set of local structural operators that appear to govern how PET behaves under multiplication.

---

## Core observation

PET behaves much more cleanly under **multiplication** than under additive exponent collision.

Two regimes must be kept separate:

- **coprime composition**
- **shared-prime update**

For coprime factors, PET composition appears to be a canonical multiset union of branches.
For shared primes, multiplication acts as a local update of an existing branch.

---

## Operator 1: `coprime_union(A, B)`

### Meaning

Combine two PET signatures coming from coprime factors.

### Rule

If `gcd(a, b) = 1`, then:

```text
signature(a*b) = canon(signature(a) ⊎ signature(b))
```

where:

- `⊎` is multiset union
- `canon(...)` is canonical sorting / normalization of the signature

### Interpretation

No collision happens.
No existing branch is modified.
The branches are simply accumulated.

---

## Operator 2: `attach_branch(S)`

### Meaning

Introduce a new prime factor with exponent `1`.

### Effect

Add a new root branch of shape:

```text
[]
```

to the signature `S`, then canonicalize.

### Arithmetic interpretation

This corresponds to multiplying by a prime `p` that is **not yet present** in the current factorization.

---

## Operator 3: `bump_branch(S, branch)`

### Meaning

Update the branch associated with a prime that is already present.

### Effect

If the current branch corresponds to exponent `k`, replace:

```text
sig(k) -> sig(k+1)
```

leaving all other branches unchanged, then canonicalize.

### Arithmetic interpretation

This corresponds to multiplying by a prime `p` that is **already present** in the current factorization.

### Important note

This operator is conceptually clear, but on a pure PET signature the branches are not labeled by concrete primes.
So this operator is best understood as a structural rule that requires extra bookkeeping if one wants to implement it directly.

---

## Operator 4: `prime_multiply(S, p)`

### Meaning

Local multiplication by a prime `p`.

### Effect

- if `p` is new: apply `attach_branch(S)`
- if `p` is already present: apply `bump_branch(S, branch_of_p)`

### Interpretation

This is the fundamental local operator of the multiplicative grammar.

---

## Derived operator: `multiply_by_factor(S, m)`

If:

```text
m = ∏ p_i^a_i
```

then multiplying by `m` can be understood as a sequence of local `prime_multiply` updates, one for each prime factor `p_i`, repeated `a_i` times.

This turns general multiplication into a sequence of local branch operations.

---

## Inverse structural operator: `partition_signature(S)`

In the coprime regime, partitioning a signature into blocks corresponds to structural coprime decomposition.

If:

```text
S = canon(A ⊎ B)
```

then `A` and `B` can be read as the PET contributions of two coprime factors.

This acts as a structural inverse to `coprime_union`.

---

## What this grammar captures

This grammar captures:

- canonical union of coprime PET components
- local branch creation for new primes
- local branch update for existing primes
- decomposition of multiplicative structure into branch-level operations

---

## What this grammar does not capture

This grammar does **not** yet capture the additive collision problem:

```text
e1 + e2
```

In particular, the experiments suggest that additive collision is **not** determined by PET signature alone, and likely requires additional arithmetic information beyond the compressed PET form.

So the current grammar should be understood as a **multiplicative PET grammar**, not as a complete PET calculus.

---

## Working interpretation

PET is not only a static anatomy of multiplicative structure.
In the multiplicative domain, it also admits a local transformation grammar:

- new prime -> attach branch
- existing prime -> bump branch
- coprime composition -> union
- general multiplication -> sequence of local updates

This appears to be the first solid layer of PET "musculature".
