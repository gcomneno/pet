# PET Vision

## Overview

PET, **Prime Exponent Tree**, is a canonical recursive representation of positive integers `N >= 2` based on prime factorization and the internal structure of exponents.

The core idea is simple:
- every integer factorizes into primes
- each exponent is represented recursively using the same logic
- the result is a canonical tree
- the representation is invertible and lossless

PET does not aim to replace classical arithmetic.
Instead, it offers a **structural perspective** on integers.

---

## General vision

PET can be understood as a project with **three distinct layers**:
1. **PET-Base**
2. **PET-Metrics**
3. **PET-Algebra**

This separation is important to avoid confusion between:
- canonical representation
- structural measurement
- experimental operations on trees

---

## 1. PET-Base

PET-Base is the rigorous core of the project.

At this level, PET is defined as a canonical recursive representation of integers `N >= 2`:
- grounded in unique prime factorization
- recursive on exponents
- invertible via `decode`
- validatable at the implementation level
- serializable in canonical JSON form

### Objective

Answer the question:
> What is the canonical PET representation of this integer?

### Core properties

- **canonicality**: the construction yields one PET for each integer
- **invertibility**: the integer can be reconstructed from its PET
- **losslessness**: the representation preserves all information needed for reconstruction

### Format and implementation properties

- **validatability**: the implementation can explicitly reject malformed or non-canonical PET documents
- **serializability**: PET has a canonical JSON representation for storage and data exchange

### Role

PET-Base is the foundational grammar of the project.
It should remain as stable, simple, and rigorous as possible.

---

## 2. PET-Metrics

PET-Metrics studies the shape of canonical PETs.

Once an integer is represented as a tree, natural questions follow:
- how deep is it?
- how branched is it?
- how wide or narrow is it?
- how symmetric is it?
- how structurally complex is it?

### Objective

Use PET as a **morphological lens** on integers.

### Examples of initial metrics

- `height`
- `node_count`
- `leaf_count`
- `max_branching`
- `verticality_ratio`

### Examples of more exploratory metrics

- branch profile by level
- recursive exponential mass
- structural asymmetry

### Role

This layer is the first real test of PET's broader value.

If PET metrics reveal non-trivial and reproducible patterns, PET can become more than an elegant encoding: it can become an exploratory tool for comparing families of integers structurally.

---

## 3. PET-Algebra

PET-Algebra is the most experimental layer.

At this level, the goal is not only to represent or measure trees, but also to explore **structural operations** on PETs.

### Possible directions

- PET composition
- grafting one PET onto leaves of another
- subtree substitution
- structural comparison
- distances between PETs
- canonical and non-canonical transformations

### Objective

Study PETs as active mathematical objects, not only as static representations.

### Important note

PET-Algebra must not alter PET-Base.

The canonical representation of an integer must remain separate from experimental operations on trees.
For this reason, grafts and compositions do not belong to the canonical base layer, but to a later experimental one.

---

## Why PET may be valuable

PET does not appear, at least for now, to solve a major classical problem.

Its potential value lies elsewhere:
- offering a canonical recursive representation
- making the exponential morphology of integers visible
- supporting the definition and study of possible structural invariants
- generating new questions about integers
- opening the way to a possible structural algebra of PET trees

In this sense, PET is not a new number theory in the traditional sense, but it may become a **platform for studying the shape of integers**.

---

## Conceptual roadmap

### Phase A — consolidate PET-Base
- formal definition
- canonical JSON format
- encode/decode
- robust validation

### Phase B — explore PET-Metrics
- define metrics
- compare families of numbers
- search for non-trivial patterns

### Phase C — experiment with PET-Algebra
- grafts
- compositions
- distances
- tree transformations

---

## Conclusion

PET is a conceptual framework with:
- a rigorous core
- a metric layer to validate empirically
- an algebraic space that remains experimental
