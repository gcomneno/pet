# PET status boundary notes

## Scope

These notes summarize the current observed status boundaries for the hybrid PET reconstruction pipeline after adding batch evaluation, exploratory scans, and focused boundary scans.

## Established pipeline status

The following end-to-end path is now exercised by a dedicated evaluation harness:

1. `partial_signature_probe.py`
2. `pet_hybrid_bridge.py`
3. `pet_hybrid_synthesize.py`
4. `pet_candidate_plan.py`
5. `pet_constructive_plan.py`

The harness records per-case outcomes and aggregate summaries by family and by observed status.

## Main observed outcomes

### 1. The end-to-end hybrid pipeline is stable on controlled and exploratory batches

Controlled and exploratory batches both validated successfully end-to-end, with no observed:
- `no_candidate`
- `mismatch`
- `planner_failed`
- `executor_failed`

This confirms that the current research-facing reconstruction loop is operational rather than a single worked example.

### 2. `perfect-power-composite-base` is real but rare

The status `perfect-power-composite-base` is observed and useful, but it appears only on a narrow subset of cases.

In those cases:
- `exact_root_anatomy = false`
- the dedicated candidate `composite-power-base-completion` rises to rank 1
- the candidate planning and constructive execution loop validates successfully

This supports keeping the dedicated status-aware handling already introduced, but does not support treating this status as common.

### 3. `prime-power-by-sympy` is frequent when the residual closes semantically as a prime power

For scans of the form `2*p^2` with tight probe budget:
- many cases close as `prime-power-by-sympy`
- those cases typically have `exact_root_anatomy = true`
- the top candidate is usually `exact-root-anatomy`

This means the status is informative, but does not currently justify a separate synthesis strategy.

### 4. `composite-non-prime-power` is the dominant difficult-status basin

Across boundary scans and exploratory scans, many difficult cases collapse into:
- `composite-non-prime-power`

This basin absorbs cases from multiple nominal families:
- composite-square-like constructions
- prime-power-edge constructions
- rough composite products
- distinct-prime products beyond simple closures

Within this basin, the observed top-ranked candidate is stably:
- `grouped-leaf-completion`

This is the strongest current empirical regularity in the difficult-case region.

## Negative results / non-rules

The scans also ruled out several naive explanations.

### 1. Nominal family does not determine observed status

The same apparent family shape can yield different observed statuses depending on arithmetic structure and probe behavior.

### 2. Prime-count alone does not determine the boundary

Distinct-prime product scans showed that the transition into `composite-non-prime-power` is not explained purely by the number of distinct primes.

### 3. Presence of factor `2` alone does not explain the boundary

A/B scans with and without `2` did not support a general rule that the factor `2` alone determines whether a case stays closed or falls into `composite-non-prime-power`.

## Current interpretation

The main discriminator is not the nominal formula of the target but the arithmetic structure of the residual that remains after bounded probe progress.

That is:
- some cases close exactly
- some cases close semantically as prime powers
- some rare cases close semantically as composite-base perfect powers
- many difficult cases remain in the broader `composite-non-prime-power` basin

## Current recommendation

Do **not** add a dedicated synthesis strategy for `composite-non-prime-power` yet.

Current evidence supports:
- keeping the existing special handling for `perfect-power-composite-base`
- keeping generic strategies for the broad `composite-non-prime-power` basin
- treating the current phase as a completed validation/mapping phase rather than a strategy-expansion phase

## Next research target

The next promising line is to further characterize internal substructure inside the `composite-non-prime-power` basin before attempting any new status-specific synthesis rule.
