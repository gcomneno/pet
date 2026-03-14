# PET Claim Status

Source of truth for the current status of the main PET claims.

| Claim                                                               | Status                             | Evidence                                                      | Source              |
|---------------------------------------------------------------------|------------------------------------|---------------------------------------------------------------|---------------------|
| PET represents every integer `N >= 2` as a recursive pet            | Definition                         | Project definition                                            | README, VISION      |
| PET uses prime factorization recursively on exponents               | Definition                         | Project definition                                            | README, VISION      |
| Exponent `1` is represented as `null` in canonical JSON             | Definition                         | Format definition                                             | README              |
| Canonical JSON node shape is `{ "p": <prime>, "e": null | [ ... ] }`| Definition                         | Format definition                                             | README              |
| PET documents are non-empty lists of nodes with strictly inc.primes | Definition                         | Format definition                                             | README              |
| PET representation is canonical (one PET per integer)               | Proved / by construction           | Unique prime factorization + deterministic recursive encoding | README, VISION, SPEC|
| PET representation is invertible                                    | Proved / by construction           | `decode(encode(N)) = N`, roundtrip tests                      | README, VISION,tests|
| PET representation is lossless                                      | Proved / by construction           | Follows from invertibility                                    | README, VISION      |
| PET JSON is the canonical machine-facing serialization              | Format / design choice             | Chosen project format                                         | README              |
| `render()` is human-facing and not intended for data exchange       | Format / design choice             | Explicit project design                                       | README              |
| Non-canonical or malformed PET documents can be rejected explicitly | Implementation property            | Validator behavior                                            | README, VISION, code/tests |
| PET-Base is the stable core layer of the project                    | Project architecture               | Explicit project structure                                    | VISION              |
| PET-Metrics studies structural properties of canonical PETs         | Project architecture               | Explicit project structure                                    | VISION              |
| PET-Algebra is a separate experimental layer                        | Project architecture               | Explicit project structure                                    | VISION              |
| PET can be used as a structural / morphological lens on integers    | Vision                             | Conceptual positioning                                        | VISION              |
| PET-Metrics may reveal non-trivial and reproducible structural patt.| Empirical / open research direction| Plausible but not yet established in docs as proved           | VISION              |
| PET may support useful structural invariants                        | Conjectural / research direction   | Motivating hypothesis                                         | VISION              |
| PET may enable classification/comparison of integer families via str| Conjectural / research direction   | Motivating hypothesis                                         | VISION              |
| PET may open the way to a structural algebra on PET trees           | Conjectural / research direction   | Explicitly future/experimental                                | VISION              |
| PET is not currently presented as a solution to a major problem     | Positioning statement              | Explicit scope statement                                      | VISION              |
