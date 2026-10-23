# Omega Divisor — Decision Lock v0.1

Status: proposed defaults for the next executable slice. These decisions settle the reserved calls without pretending that the live application was edited in this session.

## 1. Benchmark sample: target 250, fixed cohort, no padding

**Decision:** Keep the benchmark target at 250 unique, canonical graph nodes. Lock the cohort only after a completed crawl has at least 250 eligible nodes with stable IDs.

The currently reported restore contains 160 graph nodes, 228 edges, and 119 detected technologies. The separate count of 740 `.generator-card` elements is not evidence of 740 graph nodes. Do not fill the gap with UI cards, duplicate aliases, placeholders, or nodes that have not passed canonicalization.

At lock time, write an immutable manifest containing:

- schema/version and a fixed seed: `omega-divisor-benchmark-v1`;
- crawl snapshot ID and SHA-256 digest;
- all 250 canonical node IDs and their canonical source identifiers;
- source-family / category values used for stratification;
- each node's baseline assimilation state and all independently applicable gap flags;
- the deterministic selection algorithm and any underfilled stratum;
- creation timestamp and the code/version used to produce the manifest.

Select deterministically from the completed crawl snapshot. Stratify across source family and baseline assimilation state; retain every applicable gap flag as a separate label rather than forcing overlapping conditions into one class. Once locked, the cohort never rebalances. A missing or unreachable cohort member remains in the result as `missing` / `unverified`; it is not dropped and replaced. New discoveries belong to a later benchmark version.

**Pre-lock condition:** current map state is below 250, so the immediate next action is a candidate-manifest/preflight run, not locking the sample.

## 2. ρ̂ exit threshold: freeze the existing bar

**Decision:** Preserve the plan's stated strict threshold, `ρ̂ < 0.05`, for two consecutive qualifying runs. Do not tune the threshold in response to observed results.

Before applying the gate, record the exact current ρ̂ formula, numerator, denominator, missing-data treatment, and rounding. Do not silently substitute the 250-node panel for the live graph denominator if the implementation currently computes ρ̂ over the full graph. The locked panel is a regression cohort; the plan's declared metric formula remains authoritative unless a versioned, justified change is approved.

Both qualifying runs must use the same metric definition, same locked cohort version, and the same exclusion policy. A missing cohort node must be explicitly represented, not silently removed from the denominator. Log the unrounded value as well as the display value. Any formula or denominator change resets the consecutive-run count and requires a new metric version.

## 3. Ladder lane: algebraic zero-divisor calibration first

**Decision:** Use the **Cayley–Dickson zero-divisor lane**, with the sedenion stage as the first positive calibration case, because D_Ω is defined around nonzero factors whose product is zero.

Minimum evidence for this lane:

1. Use a specified multiplication convention and a reproducible, explicit pair of nonzero elements `x`, `y` for which `x·y = 0`.
2. Verify the product computationally under that convention; preserve the input pair and result as a fixture.
3. Map the factor pair to the proposed D_Ω split and retain the mapping/provenance.
4. Run Ω-closure on each resulting fragment with a declared stopping rule, iteration bound, and failure result. A chain is a closure witness only when its transition rules and terminal condition are explicit.
5. Compare against a negative-control case where the asserted zero-divisor condition does not hold.

Keep the ladder's algebraic calibration separate from claims of transfinite completion. Do not infer that a finite Cayley–Dickson test proves an ordinal/transfinite ranking. That extension needs its own formal rank function, successor relation, and external validation criterion.

## 4. Corpus home: versioned repository is canonical; browser storage is cache

**Decision:** Keep the canonical corpus contract, locked benchmark manifest, exclusion ledger, and compact run records in version control under `corpus/omega-divisor/` in the actual application repository. Browser `localStorage` remains a convenience cache and must never be the only copy of benchmark state.

Suggested layout:

```text
corpus/omega-divisor/
  README.md
  schema/
    node.schema.json
    edge.schema.json
    run.schema.json
  manifests/
    benchmark-v1.json
  exclusions.jsonl
  runs/
    README.md
  fixtures/
    cayley-dickson-sedenion-zero-divisor-v1.json
```

Keep bulky or volatile crawl caches out of the canonical benchmark definition. Each run should record the snapshot digest and export path so a result can be reconstructed. Commit compact manifests and reproducibility metadata; store large raw snapshots in an explicitly configured artifact/cache location and record their hashes.

**Repository-access caveat:** the connected GitHub default branch available in this session is `recursionlab/recursive-ai-framework`, but it does not currently contain the described `src/OMEGA_DIVISOR_PLAN.md`, `src/mother-adapt.js`, or `scratch/CURRENT_TASK.md`. Therefore this decision record is not represented as an applied commit to that repository. Place it in the actual app repository once that source is available there.

## 5. Reasoned exclusions: narrow, predeclared, and auditable

An exclusion is valid only for a predeclared scope or data-quality reason. Each record must include the canonical ID or raw locator, rule ID, reason, evidence, timestamp, and whether the exclusion affects the benchmark denominator.

Allowed categories:

- `UI_CHROME`: navigation, pagination, and page decoration that are not generator/technology entities.
- `DUPLICATE_ALIAS`: duplicate representation of an entity; preserve the alias and its mapping to the canonical entity rather than deleting its history.
- `OUT_OF_SCOPE`: demonstrably outside the frozen domain policy; quote the policy clause.
- `NO_STABLE_ID`: quarantine until canonicalization is possible; do not silently discard.
- `INACCESSIBLE`: retain a tombstone with attempts, times, and error evidence. It remains visible as unresolved unless the frozen scope policy explicitly excludes this access class before lock.
- `MALFORMED_RECORD`: preserve the raw record and validation errors; exclude only from operations that require the missing fields.

Never exclude a node merely because it is isolated, hard to crawl, unmapped, unassimilated, contradictory, low-confidence, expensive to process, or likely to worsen ρ̂. Those are target conditions, not valid exclusion reasons. No exclusions may be added retroactively to improve a benchmark score; policy changes require a new version and a before/after impact report.

## 6. Next execution order

1. Verify the live source of truth and record its code/version; resolve why the current app files are absent from the connected repository.
2. Add/export a **candidate** node manifest and report counts: raw cards, canonical nodes, aliases, eligible nodes, excluded nodes by rule, and graph nodes/edges.
3. Continue the crawl/canonicalization until at least 250 stable eligible graph nodes exist. Inspect the candidate sample and lock it with a snapshot hash.
4. Freeze and expose the exact ρ̂ formula; ensure the two-consecutive-run gate uses the same definition and cohort version.
5. Add the sedenion zero-divisor fixture and Ω-closure test as an independent lane; report pass/fail/unknown for every step.
6. Export a cold-start audit package containing the manifest, metric definition, exclusion ledger, fixture, run log, and explicit unresolved items.

## Provenance note

The supplied status text reports a live verification timestamp of `2026-10-12`. The current session date is `2026-10-11` (America/Chicago), so this timestamp is future-dated relative to this session. Preserve it as reported provenance, but verify the machine clock and actual execution timestamp before treating it as a verified event date.
