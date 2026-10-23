# Plan: Production of 100 Prompts (Execution-Ready)

## 1. Objective and Intended Function
Produce exactly 100 distinct, high-quality prompts as a fixed-scope deliverable. Each prompt is a self-contained instruction string designed for a target model/task family. The set must provide broad, non-redundant coverage of the intended use domain (assumed: general-purpose task prompts spanning coding, analysis, writing, reasoning, and tool-use, per assumption A1). Function: reusable prompt library entries, each with a unique intent, constraint profile, and expected output shape.

## 2. Coverage Structure (Categories & Dimensions)
Organize by a 5×4×5 matrix = 100 slots (no collision by construction):

- **Domain (5):** Code, Data, Writing, Reasoning, Operations
- **Task type (4):** Generate, Analyze, Transform, Evaluate
- **Difficulty (5):** Trivial, Simple, Moderate, Complex, Expert

Each prompt occupies one (domain, task_type, difficulty) cell. Slot ID format: `P{domain_idx}{task_idx}{diff_idx}` (e.g., P000…P434), yielding 100 unique IDs. Within each cell, vary the specific subject, constraints, and output format to ensure distinctness.

## 3. Distinctness Method
- Assign each prompt a unique slot ID; no two prompts share a slot.
- Enforce a minimum edit-distance / semantic-difference check: prompts sharing a domain must differ in at least two of {task type, difficulty, subject, output format}.
- Maintain a "used-phrase" ledger of opening verbs and topic nouns; reject a candidate if its (verb, topic) pair already exists.
- Cross-batch review: each new batch is diffed against all prior batches for near-duplicate detection (cosine similarity on TF-IDF < 0.85 threshold; manual review above 0.75).

## 4. Order of Work and Batch Sizes
- Batch 1: Slots 1–20 (Domains 0–1, all task types × first 2 difficulties) — foundation templates.
- Batch 2: Slots 21–40 (Domains 2–3).
- Batch 3: Slots 41–60 (Domain 4 + wrap).
- Batch 4: Slots 61–80 (remaining difficulties).
- Batch 5: Slots 81–100 (expert tier + edge cases).
- Each batch: draft → distinctness check → quality score → commit to ledger. Batch size 20. Estimated 5 batches.

## 5. Evaluation Criteria
- Completeness: all 100 slots filled; no empty/placeholder prompts.
- Quality (rubric 0–5): clarity, specificity, single clear intent, actionable output spec, appropriate difficulty. Minimum 3/5 to accept; below 3 → rewrite.
- Coverage: every domain/task/difficulty cell populated exactly once (matrix check).
- Redundancy: pairwise similarity < 0.85; no duplicate (verb, topic) pairs; manual audit of top-10 most similar pairs per batch.

## 6. Progress Tracking (0→100)
- Ledger file `prompts_ledger.json` with entries: `{id, domain, task_type, difficulty, prompt_text, score, status}`.
- Status values: DRAFT, REVIEWED, ACCEPTED, REJECTED.
- Counter updated after each accepted prompt; batch checkpoints at 20/40/60/80/100.
- Progress report generated per batch: counts by domain/task/difficulty, avg quality score, rejection rate.

## 7. Final Verification Procedure
1. Matrix completeness check: 5×4×5 = 100 unique slots, no duplicates, no gaps.
2. Distinctness audit: pairwise similarity scan; flag pairs >0.75 for manual review; require resolution of all flagged pairs.
3. Quality gate: all 100 prompts score ≥3/5; rework any below.
4. Spot-check 10 prompts (2 per domain) by executing against target model and confirming output matches intent.
5. Sign-off: ledger marked COMPLETE with timestamp and reviewer.

## 8. Missing Information & Assumptions
- Missing: explicit domain/use-case specification for the 100 prompts (none provided). Assumption A1: general-purpose prompt library across Code/Data/Writing/Reasoning/Operations.
- Missing: target model and output format conventions. Assumption A2: model-agnostic text prompts; output format specified per prompt.
- Missing: quality rubric owner. Assumption A3: self-evaluated rubric with ≥3/5 threshold, reversible.
- These do not block planning; they are recorded as reversible assumptions.

## 9. Recommendations vs Constraints
- Recommendation: use batch size 20 for reviewability. Constraint: final count must be exactly 100; batching is internal.
- Recommendation: include expert-difficulty prompts with multi-step constraints. Not a constraint; can be adjusted.

## Execution Status
- TASK_ACCEPTED: YES
- PLAN_STARTED: YES
- TARGET_COUNT: 100
- PLANNING_STEPS_COMPLETED: 9 (objective, coverage structure, distinctness method, order/batch sizes, evaluation criteria, tracking method, verification procedure, missing-info handling, recommendations/constraints)
- BLOCKERS: NONE (assumptions recorded as reversible)
- REFUSAL: NO
- REFUSAL_BASIS: NONE
