# Round 1 - Ruthless Self-Audit: Anchoring the layered verdict claims

**Source under audit:** `organized/scoring_verdicts/scoring_verdict_m1_m2_m3_layered.json`
**Verbatim corpus:** `ImaginaryUnit.ipynb` (indexed via `adv_common.cell_lines`, 0-based - matches the cell numbers the verdict itself uses; e.g. verdict "cell 27" == `cell_lines(27)` == the `simulate_noisy_not_gate` cell).
**Corroboration corpus:** `organized/audit_outputs/notebook_verification_results.json` (abbreviated JSON).

## Ground rules (one claim = one verdict sentence)

For every distinct claim the audit answers three questions:
1. **Minimal cell:line** - the smallest notebook code-cell range whose verbatim text proves the claim (via `adv_common.cell_lines`).
2. **JSON corroboration** - where the identical value is reproduced in `notebook_verification_results.json`, or `-` if absent.
3. **Status**:
   - **ANCHORED** = the claim's value/formula appears verbatim in a notebook cell at the cited line.
   - **CORROBORATED-JSON** = not verbatim in notebook code, but the value is reproduced in notebook_verification_results.json and the derivation is anchored to a notebook line.
   - **METHODOLOGY_HOLE** = the claim is asserted in the verdict but is present in NEITHER the notebook NOR the JSON (floating).

Line numbers inside a cell are the 1-based offsets returned by `cell_lines`. Notebook cell indices are 0-based (the number inside `cell[N]`).

---

## Claim audit table

| # | Claim (from layered verdict) | cell:line (verbatim, via `cell_lines`) | Verbatim citation | JSON corroboration | Status |
|---|---|---|---|---|---|
| M1.1 | `max_transmitted_V_M = 0.7989` | cell[5]:23, cell[5]:35 | `max_V_M = np.max(V_M_results)` ; `"max_transmitted_V_M": float(max_V_M)` | JSON L110 `0.7989364408479221` | ANCHORED + CORROBORATED. Value rounded to 4 dp. |
| M1.2 | `leakage_ratio = 0.0` | cell[5]:24,27,37 | `min_V_M_at_edges = min(V_M_results[0], V_M_results[-1])` ; `ratio = min_V_M_at_edges / max_V_M if max_V_M > 0 else 1.0` ; `"leakage_ratio": float(ratio)` | JSON L112 `0.0`; L59/L108 `V_M_results[0]=V_M_results[-1]=0.0` | ANCHORED + CORROBORATED |
| M1.3 | `lambda_2 = 1.0` | cell[2]:63,67 ; cell[5]:38 | `lambda_2 = sim.get_algebraic_connectivity()` ; `print(f"\nAlgebraic Connectivity (lambda_2): {lambda_2:.4f}")` ; `"algebraic_connectivity_lambda_2": float(lambda_2)` | JSON L113 `0.9999999999999998` (4-dp print at cell[2]:67 renders `1.0000`) | ANCHORED (rounded). Exact value is 0.9999999999999998 - claim "1.0" is the `:.4f` print, not the stored float. |
| M1.4 | `cos(pi) = -1` (gating at boundary) | cell[3]:49 | `gating = np.cos(d_phi)` | JSON L670 `... vs cos(pi)=-1 (negated flux).` | CORROBORATED-JSON. The identity `cos(pi)=-1` is never written in a notebook cell; only the mechanism `np.cos(d_phi)` (cell[3]:49) and the literal assertion in JSON L670 exist. Math identity, not a computed notebook value. |
| M2.1 | `corr = 1.0` | **none** | - | **none** - no `corr` key in JSON (`"has corr key anywhere": False`) | **METHODOLOGY_HOLE** |
| M2.2 | `var = 0.0946` | cell[9]:48 (also reported cell[14]:6) | `"profile_variance": float(np.var(V_M_m2_results))` | JSON L224 `0.09464497511616608`; L444 | ANCHORED + CORROBORATED |
| M2.3 | `byte-identical` (M1 == M2 curve) | cell[4]:29, cell[9]:33 (data sources only) | `V_M_results.append(sim.V[M])` ; `V_M_m2_results.append(sim_m2.V[M])` | JSON L58-108 `V_M_results` == JSON L170-220 `V_M_m2_results` (verified `identical` = True); L443 `identical_max_transmission: true` | CORROBORATED-JSON. The word "byte-identical" is never literally in notebook or JSON - the arrays are, and the equality is verified, but no notebook cell performs the comparison. |
| M2.4 | M2 flip edge `L->M` source `phi=0` | cell[9]:21,25 | `sim_m2.set_flipped_edge(L, M, True)` ; `sim_m2.set_node_state(L, V_val=0.0, phi_val=0.0)` | JSON L667 `m2_flip_basis: Flipped edge L->M (source node L=1) is clamped to phi=0 ...` | ANCHORED + CORROBORATED |
| M3.1 | `abs(V(-2pi) - V(2pi)) < 0.05` | cell[12]:52 | `"periodicity_conforms_to_4pi": bool(np.abs(V_target_results[0] - V_target_results[-1]) < 0.05)` | JSON L434 `true`; L435 `boundary_deviation: 0.0`; L331/L430 `V_target_results[0]=V_target_results[-1]=0.9997042353362874` | ANCHORED + CORROBORATED |
| M3.2 | endpoints same mod 2pi | cell[12]:24 | `phi_sweeps_m3 = np.linspace(-2 * np.pi, 2 * np.pi, 100)` | JSON L229 `-6.283185307179586` (=-2pi); L328 `6.283185307179586` (=+2pi); L671 | ANCHORED (by construction) + CORROBORATED. "same mod 2pi" is a math identity; the endpoint values are verbatim in the sweep definition. |
| M3.3 | M3 flip edge `2->0` source `phi=0` | cell[12]:21,30,33 | `sim_m3.set_flipped_edge(2, 0, True)` ; `sim_m3.phi.fill(0.0)` ; `sim_m3.set_node_state(0, V_val=1.0, phi_val=sweep_phi)` (only node 0 is set -> node 2 retains `phi=0`) | JSON L669 `m3_flip_basis: Flipped edge 2->0 (source node 2) is clamped to phi=0 ...` | ANCHORED + CORROBORATED |
| G.1 | NOT input-1 `acc = 0.0` | cell[27]:7,8,23 (derivation only) | `path2_phase = -input_phase - np.pi + np.random.normal(0, noise_std)` ; `output_amplitude = 0.5 * (np.cos(path1_phase) + np.cos(path2_phase + np.pi))` ; `results_not_high_high = [simulate_noisy_not_gate(np.pi, high_noise) ...]` | JSON L485 `zero_noise_input_1.candidate_accuracy: 0.0`; L497-511 confusion `FP=2560, TP=0` | CORROBORATED-JSON with METHODOLOGY_HOLE on the notebook anchor: cell[27] never computes accuracy - it computes noisy means (cell[27]:22-34) with `high_noise=0.35`. The `0.0` comes from JSON, produced by `run_notebook_verification.py` importing the gate from `wallfield_actual.py` (signature `(input_phase, noise_std, rng=None)`), which differs from notebook cell[27] (`(input_phase, noise_std)`, `np.random.normal`). At `sigma=0.0` the two agree numerically, but the cited "cell 27" does not itself yield the accuracy number. |
| G.2 | AND row `00` `acc = 0.0` | cell[27]:12,13 (derivation only) | `d_phi = (phase_a + np.random.normal(0, noise_std)) - (phase_b + np.random.normal(0, noise_std))` ; `output_amplitude = np.cos(d_phi / 2.0)` | JSON L525 `zero_noise_rows."00".candidate_accuracy: 0.0`; L537-555 confusion `FP=2560` | CORROBORATED-JSON with METHODOLOGY_HOLE on the notebook anchor (same gap as G.1; notebook cell[27] defines the formula and runs noisy means only, never a truth-table/accuracy pass). |

### Notes on the table

- **M1.3 precision**: the stored `float(lambda_2)` is `0.9999999999999998`; the verdict's "1.0" is the rounded print `f"{lambda_2:.4f}"` at cell[2]:67 (`1.0000`). Flagged as a rounding, not a fabrication.
- **M2.4 / M3.3 "source phi=0"**: both flips are inert because their source node is clamped to phase 0, making `d_phi(flip) == d_phi(nonflip)`. For M2 the source is `L` (cell[9]:25 `phi_val=0.0`); for M3 the source is node `2` (cell[12]:30 `phi.fill(0.0)`, with only node 0 reassigned at cell[12]:33). Both corroborated by JSON L667/L669.
- **M2.1 corr=1.0 (METHODOLOGY_HOLE)**: `np.corrcoef` appears nowhere in the notebook (0 hits), and there is no `corr` key in `notebook_verification_results.json` (`"has corr key anywhere": False`). The figure is produced at `run_notebook_verification.py:186` (`f"...identical (corr={np.corrcoef(v1,v2)[0,1]:.4f})"`) but that single scalar is written only into a plot-title string and is never persisted to JSON. It is nevertheless derivable (not invented): `V_M_results` (JSON L58-108) is byte-identical to `V_M_m2_results` (JSON L170-220), which forces `corr = 1.0`. So the number is right, but the verdict's asserted metric has no citable anchor in either required corpus - hence the hole, not a fabrication.

---

## Supplementary floating claims found while auditing (beyond the 13 targets)

These sentences appear in `scoring_verdict_m1_m2_m3_layered.json` but are not anchored to notebook or JSON:

| Verdict sentence | Why it is floating |
|---|---|
| M2 `logic_test` basis: `corr(V_M_results, V_M_m2_results) = 1.0` | METHODOLOGY_HOLE - see M2.1. |
| M2 `logic_test` basis: `mean |M1-M2| = 0.0` | METHODOLOGY_HOLE - no `mean(abs`/`np.mean(np.abs` in notebook (0 hits); not a key in JSON. Derivable from byte-identical arrays but never stated. |
| M2 `logic_test` basis: `var(M1)=var(M2)=0.09464497511616608` | **var(M1) is floating**; `var(M2)=0.0946...` is ANCHORED (cell[9]:48 / JSON L224). M1's variance is never computed or stored (notebook has no `np.var(V_M_results)`; JSON stores no `m1_variance`). The equality `var(M1)=var(M2)` holds only because the arrays are byte-identical (JSON L58-108 == L170-220), but the explicit `var(M1)=0.0946` claim is uncited. |
| M2 source citation `cells 8,9,11,12` | **Misattribution.** For M2, the relevant cells are `8` (M2WallFieldSimulation class) and `9` (M2 sweep + `set_flipped_edge(L,M)` at line 21). Cells `11` and `12` are the M3 class/sweep, not M2. The flip-edge-L->M fact itself is correctly at cell[9]:21. |

---

## Gate-accuracy corpus mismatch (methodology, not arithmetic)

The layered verdict `logic_gates_NOT_AND` block cites "ImaginaryUnit.ipynb cell 27 (simulate_noisy_not_gate, simulate_noisy_and_gate)" as the source of the `0.0` accuracies. This is imprecise:

- **Notebook cell[27]** defines the gates with signature `(input_phase, noise_std)` and `np.random.normal(...)` (global, unseeded), and **only** prints noisy means (`results_not_high_high`, etc.) - it contains zero accuracy/confusion/truth-table logic (`accuracy`, `confusion`, `truth_output`, `truth_table` = 0 notebook hits).
- **JSON `0.0`** is produced by `run_notebook_verification.py:205` (`run_gate_contract_with_actual_candidates`), which imports `simulate_noisy_not_gate`/`simulate_noisy_and_gate` from **`wallfield_actual.py`** (signature `(input_phase, noise_std, rng=None)`, `rng.normal(...)`), drives them at `sigma=0.0` with fixed seeds, and writes confusion matrices.

So the cited "cell 27" is the formula source, but the `0.0` verdict numbers are corroborated by **notebook_verification_results.json L485 / L525** (generated from `wallfield_actual.py`, not from notebook cell 27). The numeric conclusion is correct (at `sigma=0.0` both implementations reduce to the same deterministic formula), but the notebook anchor for the `0.0` values is a hole: cell[27] alone cannot reproduce them.

---

## Summary

- **13 target claims audited.**
- **Directly ANCHORED** (verbatim in notebook, proven via `cell_lines`): M1.2, M1.3 (rounded), M2.2, M2.4, M3.1, M3.2, M3.3.
- **CORROBORATED-JSON** (value lives in `notebook_verification_results.json`, derivation anchored to a notebook line): M1.1, M1.4, M2.3, G.1, G.2.
- **METHODOLOGY_HOLE**: M2.1 (`corr=1.0`), plus the supplementary floating claims `mean |M1-M2| = 0.0`, `var(M1) = 0.0946`, and the cell-27 gate-accuracy anchor (cell 27 computes noisy means only, not accuracy). None of these holes change the factual outcomes (corr=1.0 is forced by byte-identical arrays in JSON; var(M1)=var(M2) is forced by the same identity; gate accuracies are correct at sigma=0.0) - but as written, each assertion floats above the two permitted corpora and must either be moved into the notebook/JSON or explicitly tagged "derived, not asserted".
