# Experiment 1 — scorecard

## Scope

This scorecard is the compact verdict layer for Experiment 1.

It does not replace the benchmark report.
It exists to force a short, explicit answer about what PET can already claim and what it still cannot claim.

## Families

- Perfect
- Primorials
- Hamming (5-smooth)
- HighlyComposite

## Scorecard fields

For each family, record:

- internal compactness
- internal variability
- structural distinctiveness
- overlap risk
- confidence level

For each family pair, record:

- average separation signal
- minimum-distance overlap risk
- verdict

## Family scorecard template

| family | compactness | variability | distinctiveness | overlap risk | confidence | verdict |
|---|---|---|---|---|---|---|
| Perfect | high / medium / low | high / medium / low | high / medium / low | high / medium / low | high / medium / low | one-line verdict |
| Primorials | high / medium / low | high / medium / low | high / medium / low | high / medium / low | high / medium / low | one-line verdict |
| Hamming | high / medium / low | high / medium / low | high / medium / low | high / medium / low | high / medium / low | one-line verdict |
| HighlyComposite | high / medium / low | high / medium / low | high / medium / low | high / medium / low | high / medium / low | one-line verdict |

## Pairwise scorecard template

| pair | average separation | overlap risk | confidence | verdict |
|---|---|---|---|---|
| Perfect vs Primorials | high / medium / low | high / medium / low | high / medium / low | one-line verdict |
| Perfect vs Hamming | high / medium / low | high / medium / low | high / medium / low | one-line verdict |
| Perfect vs HighlyComposite | high / medium / low | high / medium / low | high / medium / low | one-line verdict |
| Primorials vs Hamming | high / medium / low | high / medium / low | high / medium / low | one-line verdict |
| Primorials vs HighlyComposite | high / medium / low | high / medium / low | high / medium / low | one-line verdict |
| Hamming vs HighlyComposite | high / medium / low | high / medium / low | high / medium / low | one-line verdict |

## Interpretation rules

Use the scorecard conservatively.

Rules:

1. high separation does not mean perfect classification
2. low minimum distance means real overlap risk, even when averages look good
3. bounded evidence should not be inflated into asymptotic claims
4. a mixed result is still a valid result

## Intended use

This document is the shortest decision layer for Experiment 1.

It should answer, at a glance:

- which family looks structurally tightest
- which family looks structurally widest
- which pair looks best separated
- where PET still shows overlap and ambiguity
- whether the benchmark supports a cautious positive claim or only a weak descriptive claim
