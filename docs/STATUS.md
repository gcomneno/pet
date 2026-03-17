# PET Claim Status

Source of truth for the current status of the main PET claims.

This document separates:
- project definitions
- properties that hold by construction
- format choices
- implementation properties
- empirically supported bounded results
- project architecture
- conceptual positioning
- conjectural / future directions

It is intentionally conservative: a claim should not be presented as stronger than the evidence currently supporting it.

## Status legend

- **Definition** — part of the declared PET model or syntax
- **Proved / by construction** — follows directly from the canonical construction
- **Format / design choice** — chosen project encoding or presentation decision
- **Implementation property** — behavior provided by code and validation logic
- **Empirically supported / bounded** — observed and documented on explicit finite ranges
- **Project architecture** — structural role inside the PET project
- **Vision / positioning** — conceptual framing of the project
- **Conjectural / research direction** — plausible or motivating direction, not established as general theory

| Claim | Status | Evidence | Source |
|---|---|---|---|
| PET represents every integer `N >= 2` as a recursive PET | Definition | Core project definition | README, VISION, SPEC |
| PET uses prime factorization recursively on exponents | Definition | Core project definition | README, VISION, SPEC |
| Exponent `1` is represented as `null` in canonical JSON | Format / design choice | Chosen canonical JSON encoding | README |
| Canonical JSON node shape is `{ "p": <prime>, "e": null | [ ... ] }` | Format / design choice | Chosen canonical JSON encoding | README |
| PET documents are non-empty lists of nodes with strictly increasing primes | Definition | Canonical PET syntax and normal form | README, SPEC |
| PET representation is canonical (one PET per integer) | Proved / by construction | Unique prime factorization + deterministic recursive encoding | README, VISION, SPEC |
| PET representation is invertible | Proved / by construction | `decode(encode(N)) = N`; explicit inverse role in PET-Base | VISION, SPEC |
| PET representation is lossless | Proved / by construction | Follows from invertibility | README, VISION, SPEC |
| PET JSON is the canonical machine-facing serialization | Format / design choice | Explicit project serialization choice | README, VISION |
| `render()` is human-facing and not intended for data exchange | Format / design choice | Explicit separation between machine format and human rendering | README |
| Non-canonical or malformed PET documents can be rejected explicitly | Implementation property | Validation behavior is part of the implementation layer | VISION |
| PET-Base is the stable core layer of the project | Project architecture | Explicit project structure | VISION |
| PET-Metrics studies structural properties of canonical PETs | Project architecture | Explicit project structure | VISION |
| PET-Algebra is a separate experimental layer | Project architecture | Explicit project structure | VISION |
| PET can be used as a structural / morphological lens on integers | Vision / positioning | Conceptual role stated explicitly | VISION |
| PET-Metrics already shows reproducible bounded structural patterns on explicit scan ranges | Empirically supported / bounded | Documented bounded distributions, invariants, and reports on finite ranges | README, SPEC |
| PET may support useful structural invariants beyond current bounded evidence | Conjectural / research direction | Motivating research direction beyond what is already bounded and documented | VISION |
| PET may enable classification or comparison of integer families via structural metrics | Conjectural / research direction | Motivating research direction; current evidence is partial and bounded | VISION, SPEC |
| PET may open the way to a structural algebra on PET trees | Conjectural / research direction | Explicitly experimental future direction | VISION, SPEC |
| PET is not currently presented as a solution to a major classical problem | Vision / positioning | Explicit scope statement | VISION |

## Notes

- Claims about **canonicality**, **invertibility**, and **losslessness** belong to PET-Base and should be treated as the strongest part of the project documentation.
- Claims about **metrics**, **invariants**, and **family comparison** should be read with range-awareness: some are already supported on explicit finite ranges, but that does not automatically promote them to general theorems.
- Claims about **PET-Algebra** are intentionally split: some concrete operations may be specified in `SPEC.md`, but the broader algebraic significance of the layer remains exploratory.
