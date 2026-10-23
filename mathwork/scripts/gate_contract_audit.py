#!/usr/bin/env python3
"""Standalone, credit-free truth-table/noise audit for phase-encoded logic.

IMPORTANT SCOPE:
- This is a reference contract harness and a set of negative controls.
- It is NOT a reproduction of the unavailable original Colab notebook.
- `not_phase_reference` and `and_truth_table_reference` establish the expected
  Boolean contract using a simple phase encoding: bit 0 -> phase 0; bit 1 -> pi.
- `xnor_phase_candidate` is a negative control matching the described pattern
  cos((phi_a - phi_b)/2) with HIGH when phases agree; it is XNOR-like, not AND.
- `always_high_not_control` is a negative control matching the observed failure
  signature that both NOT inputs produce HIGH. It is not claimed to reproduce
  the exact missing legacy formula.

Run with: python gate_contract_audit.py
Dependencies: numpy, matplotlib.
"""
from __future__ import annotations
import json
import math
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent
# Predeclared audit seeds. They are fixed for reproducibility and are not tuned
# per gate/noise condition to obtain a passing result.
SEEDS = (73129, 84221, 95317, 106487, 117503)
NOISE_SIGMAS = (0.0, 0.10, 0.25, 0.50, 0.75, 1.00, 1.25)  # radians, input and output phase noise
TRIALS_PER_ROW_PER_SEED = 512


def encode_bit(bits: np.ndarray) -> np.ndarray:
    """Encode 0 -> 0 rad and 1 -> pi rad."""
    return np.pi * np.asarray(bits, dtype=float)


def wrap_phase(phi: np.ndarray) -> np.ndarray:
    return np.mod(phi, 2.0 * np.pi)


def decode_phase(phi: np.ndarray) -> np.ndarray:
    """Decode the phase half-plane: cos(phi)<0 means bit 1; else bit 0."""
    return (np.cos(wrap_phase(phi)) < 0.0).astype(np.int8)


def not_phase_reference(phi_in: np.ndarray, output_noise: np.ndarray) -> np.ndarray:
    """Reference NOT as a pi phase shift followed by channel noise/readout."""
    return decode_phase(phi_in + np.pi + output_noise)


def always_high_not_control(phi_in: np.ndarray, output_noise: np.ndarray) -> np.ndarray:
    """Failure-signature control: outputs HIGH for either logical input."""
    del output_noise
    return np.ones_like(np.asarray(phi_in), dtype=np.int8)


def and_truth_table_reference(phi_a: np.ndarray, phi_b: np.ndarray, output_noise: np.ndarray) -> np.ndarray:
    """Reference AND: decode both inputs, apply the exact truth table, re-encode."""
    a = decode_phase(phi_a)
    b = decode_phase(phi_b)
    ideal_out_phase = encode_bit(a & b)
    return decode_phase(ideal_out_phase + output_noise)


def xnor_phase_candidate(phi_a: np.ndarray, phi_b: np.ndarray, output_noise: np.ndarray) -> np.ndarray:
    """Negative control: phase agreement score, i.e. XNOR-like behavior.

    This tests the candidate family described as cos(delta_phi/2), HIGH when
    inputs agree. A score threshold of 0.5 gives a concrete, explicit decision
    rule. It is not represented as the user's exact missing implementation.
    """
    agreement_score = np.cos(0.5 * (phi_a - phi_b))
    predicted_high = (agreement_score >= 0.5).astype(np.int8)
    return decode_phase(encode_bit(predicted_high) + output_noise)


def confusion(actual: np.ndarray, predicted: np.ndarray) -> dict:
    actual = np.asarray(actual, dtype=np.int8).reshape(-1)
    predicted = np.asarray(predicted, dtype=np.int8).reshape(-1)
    tn = int(np.sum((actual == 0) & (predicted == 0)))
    fp = int(np.sum((actual == 0) & (predicted == 1)))
    fn = int(np.sum((actual == 1) & (predicted == 0)))
    tp = int(np.sum((actual == 1) & (predicted == 1)))
    total = tn + fp + fn + tp
    return {
        "labels": {"actual_rows": [0, 1], "predicted_columns": [0, 1]},
        "matrix": [[tn, fp], [fn, tp]],
        "TN": tn, "FP": fp, "FN": fn, "TP": tp,
        "n": total,
        "accuracy": (tn + tp) / total if total else None,
        "false_positive_rate": fp / (fp + tn) if fp + tn else None,
        "false_negative_rate": fn / (fn + tp) if fn + tp else None,
    }


def run_not_sigma(sigma: float) -> dict:
    rows = []
    for seed in SEEDS:
        rng = np.random.default_rng(seed + int(round(sigma * 10000)))
        x = np.repeat(np.array([0, 1], dtype=np.int8), TRIALS_PER_ROW_PER_SEED)
        rng.shuffle(x)
        phi_in = encode_bit(x) + rng.normal(0.0, sigma, size=x.size)
        output_noise = rng.normal(0.0, sigma, size=x.size)
        correct = not_phase_reference(phi_in, output_noise)
        bad = np.ones_like(x)
        rows.append((x, correct, bad))
    actual = np.concatenate([np.logical_not(r[0]).astype(np.int8) for r in rows])
    ref = np.concatenate([r[1] for r in rows])
    bad = np.concatenate([r[2] for r in rows])
    per_input = {}
    for input_bit in (0, 1):
        per_input[str(input_bit)] = {
            "n": int(np.sum(np.concatenate([r[0] for r in rows]) == input_bit)),
            "reference_accuracy": float(np.mean(ref[(np.concatenate([r[0] for r in rows])) == input_bit] == (1 - input_bit))),
            "always_high_accuracy": float(np.mean(bad[(np.concatenate([r[0] for r in rows])) == input_bit] == (1 - input_bit))),
        }
    x_all = np.concatenate([r[0] for r in rows])
    return {
        "sigma_rad": sigma,
        "n": int(actual.size),
        "reference": confusion(actual, ref),
        "always_high_negative_control": confusion(actual, bad),
        "per_input": per_input,
        "input_counts": {str(k): int(np.sum(x_all == k)) for k in (0, 1)},
    }


def run_and_sigma(sigma: float) -> dict:
    all_inputs = []
    all_actual = []
    all_ref = []
    all_xnor = []
    row_results = {}
    for a_bit, b_bit in ((0, 0), (0, 1), (1, 0), (1, 1)):
        row_inputs = []
        row_truth = []
        row_ref = []
        row_xnor = []
        for seed in SEEDS:
            rng = np.random.default_rng(seed + 1000000 + int(round(sigma * 10000)) + a_bit * 101 + b_bit * 313)
            n = TRIALS_PER_ROW_PER_SEED
            a = np.full(n, a_bit, dtype=np.int8)
            b = np.full(n, b_bit, dtype=np.int8)
            phi_a = encode_bit(a) + rng.normal(0.0, sigma, size=n)
            phi_b = encode_bit(b) + rng.normal(0.0, sigma, size=n)
            output_noise_ref = rng.normal(0.0, sigma, size=n)
            output_noise_xnor = rng.normal(0.0, sigma, size=n)
            ref = and_truth_table_reference(phi_a, phi_b, output_noise_ref)
            xnor = xnor_phase_candidate(phi_a, phi_b, output_noise_xnor)
            truth = np.full(n, a_bit & b_bit, dtype=np.int8)
            row_inputs.append(np.column_stack([a, b]))
            row_truth.append(truth); row_ref.append(ref); row_xnor.append(xnor)
        inp = np.concatenate(row_inputs)
        truth = np.concatenate(row_truth)
        ref = np.concatenate(row_ref)
        xnor = np.concatenate(row_xnor)
        row_results[f"{a_bit}{b_bit}"] = {
            "n": int(truth.size),
            "truth_output": int(a_bit & b_bit),
            "reference_accuracy": float(np.mean(ref == truth)),
            "xnor_candidate_accuracy": float(np.mean(xnor == truth)),
            "reference_confusion": confusion(truth, ref),
            "xnor_candidate_confusion": confusion(truth, xnor),
        }
        all_inputs.append(inp); all_actual.append(truth); all_ref.append(ref); all_xnor.append(xnor)
    actual = np.concatenate(all_actual)
    ref = np.concatenate(all_ref)
    xnor = np.concatenate(all_xnor)
    return {
        "sigma_rad": sigma,
        "n": int(actual.size),
        "truth_table_rows": row_results,
        "reference": confusion(actual, ref),
        "xnor_phase_negative_control": confusion(actual, xnor),
        "row_order": ["00", "01", "10", "11"],
    }


def make_plot(results: dict) -> Path:
    sigmas = [r["sigma_rad"] for r in results["NOT"]]
    not_ref = [r["reference"]["accuracy"] for r in results["NOT"]]
    not_bad = [r["always_high_negative_control"]["accuracy"] for r in results["NOT"]]
    and_ref = [r["reference"]["accuracy"] for r in results["AND"]]
    and_xnor = [r["xnor_phase_negative_control"]["accuracy"] for r in results["AND"]]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    axes[0].plot(sigmas, not_ref, marker="o", label="NOT phase reference")
    axes[0].plot(sigmas, not_bad, marker="s", linestyle="--", label="Always-HIGH failure control")
    axes[0].set_title("NOT: exact Boolean contract")
    axes[0].set_xlabel("Input/output phase-noise σ (radians)")
    axes[0].set_ylabel("Accuracy")
    axes[0].set_ylim(-0.03, 1.03)
    axes[0].grid(True, alpha=.25); axes[0].legend()
    axes[1].plot(sigmas, and_ref, marker="o", label="AND truth-table reference")
    axes[1].plot(sigmas, and_xnor, marker="s", linestyle="--", label="Cosine agreement / XNOR control")
    axes[1].set_title("AND: four balanced input rows")
    axes[1].set_xlabel("Input/output phase-noise σ (radians)")
    axes[1].set_ylabel("Accuracy")
    axes[1].set_ylim(-0.03, 1.03)
    axes[1].grid(True, alpha=.25); axes[1].legend()
    fig.suptitle("Standalone gate-contract stress test — reference harness, not original Colab reproduction")
    fig.tight_layout()
    path = OUT / "gate_noise_accuracy.png"
    fig.savefig(path, dpi=170, bbox_inches="tight")
    plt.close(fig)
    return path


def main() -> None:
    not_results = [run_not_sigma(float(s)) for s in NOISE_SIGMAS]
    and_results = [run_and_sigma(float(s)) for s in NOISE_SIGMAS]
    result = {
        "title": "Standalone phase-encoded gate contract audit",
        "status": "REFERENCE_HARNESS_ONLY_NOT_ORIGINAL_NOTEBOOK_VALIDATION",
        "truth_tables": {
            "NOT": {"0": 1, "1": 0},
            "AND": {"00": 0, "01": 0, "10": 0, "11": 1},
            "XNOR_negative_control": {"00": 1, "01": 0, "10": 0, "11": 1},
        },
        "phase_encoding": {"bit_0_rad": 0.0, "bit_1_rad": math.pi, "decode_rule": "bit=1 iff cos(phi)<0"},
        "experiment": {
            "fixed_seeds": list(SEEDS),
            "trials_per_truth_row_per_seed": TRIALS_PER_ROW_PER_SEED,
            "noise_sigma_radians": list(NOISE_SIGMAS),
            "noise_model": "independent zero-mean Gaussian phase noise on each input and output phase; phase readout by cosine half-plane",
            "comparators": ["correct NOT phase shift reference", "always-HIGH NOT failure-signature control", "AND Boolean truth-table reference", "cosine phase-agreement/XNOR negative control"],
        },
        "NOT": not_results,
        "AND": and_results,
    }
    json_path = OUT / "gate_noise_results.json"
    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    plot_path = make_plot(result)

    baseline_not = not_results[0]
    baseline_and = and_results[0]
    robust_not = not_results[3]  # sigma 0.50
    robust_and = and_results[3]
    row_at_zero = baseline_and["truth_table_rows"]
    report = f'''# Gate-contract audit — standalone reference harness

## Purpose and boundary

This run executes locally with no Colab credits. It implements an explicit phase-bit encoding and checks the exact Boolean contracts under a declared noise sweep. **It does not reproduce or validate the missing original Colab notebook.** The negative controls demonstrate recognizable failure modes; their behavior must not be presented as the exact legacy implementation unless its source formula is supplied.

## Contract

- Encoding: bit 0 → phase 0; bit 1 → phase π.
- Decode: bit 1 iff `cos(phase) < 0`.
- NOT: apply a π phase shift, then decode after output-channel noise.
- AND: decode both input phases, apply the exact Boolean AND truth table, encode output, then decode after output-channel noise. This is a **logic reference**, not evidence for a new physical phase-coupling mechanism.
- Negative control for NOT: always outputs HIGH, matching the reported failure signature of both inputs producing HIGH.
- Negative control for AND: threshold `cos((phi_a - phi_b)/2) >= 0.5`, a phase-agreement/XNOR-like rule.

AND rows are balanced independently: `00`, `01`, `10`, `11` each receive {len(SEEDS)*TRIALS_PER_ROW_PER_SEED} trials per noise level. NOT inputs are balanced. Each noise level is rerun using the fixed, predeclared seeds in the JSON. Noise is Gaussian phase perturbation on each input and output phase.

## Key checks

- At zero noise, NOT reference accuracy: **{baseline_not['reference']['accuracy']:.3f}**; always-HIGH control accuracy: **{baseline_not['always_high_negative_control']['accuracy']:.3f}**.
- At zero noise, AND reference accuracy: **{baseline_and['reference']['accuracy']:.3f}**; cosine/XNOR negative-control accuracy against AND: **{baseline_and['xnor_phase_negative_control']['accuracy']:.3f}**.
- At σ = 0.50 rad, NOT reference accuracy: **{robust_not['reference']['accuracy']:.3f}**; always-HIGH control accuracy: **{robust_not['always_high_negative_control']['accuracy']:.3f}**.
- At σ = 0.50 rad, AND reference accuracy: **{robust_and['reference']['accuracy']:.3f}**; cosine/XNOR negative-control accuracy: **{robust_and['xnor_phase_negative_control']['accuracy']:.3f}**.
- Zero-noise AND candidate output correctness by row: {', '.join('{}: {:.3f}'.format(row, v['reference_accuracy']) for row, v in row_at_zero.items())}.

## Confusion matrices

Matrix convention is `[[TN, FP], [FN, TP]]`; rows are actual output labels (0 then 1), columns are predicted output labels (0 then 1). Full matrices at every noise level are in `gate_noise_results.json`.

### Zero-noise NOT

Reference: `{baseline_not['reference']['matrix']}`

Always-HIGH failure control: `{baseline_not['always_high_negative_control']['matrix']}`

### Zero-noise AND

Reference: `{baseline_and['reference']['matrix']}`

Cosine/XNOR negative control: `{baseline_and['xnor_phase_negative_control']['matrix']}`

## Verdict

**Reference-contract checks pass; legacy implementation remains unverified.** The test harness distinguishes a correct Boolean gate from explicit failure controls and produces full confusion matrices under noise. This is the smallest local proof that the testing machinery can detect the named defects. The original notebook's formulas, seeds, plots, and verdicts must still be plugged into this harness before any claim about the original implementation can change from unverified to tested.

## Integration adapter points

Replace the implementations of `not_phase_reference` and `and_truth_table_reference` with wrappers around the actual candidate functions once those source cells are available. Do not replace the truth-table target or acceptance criteria with candidate outputs. Preserve row balance, fixed seeds, confusion matrix convention, and the noise sweep.
'''
    (OUT / "gate_contract_report.md").write_text(report, encoding="utf-8")
    print(json.dumps({
        "report": str(OUT / "gate_contract_report.md"),
        "results": str(json_path),
        "plot": str(plot_path),
        "zero_noise_NOT_reference_accuracy": baseline_not["reference"]["accuracy"],
        "zero_noise_NOT_always_high_accuracy": baseline_not["always_high_negative_control"]["accuracy"],
        "zero_noise_AND_reference_accuracy": baseline_and["reference"]["accuracy"],
        "zero_noise_AND_XNOR_control_accuracy": baseline_and["xnor_phase_negative_control"]["accuracy"],
        "sigma_0_5_NOT_reference_accuracy": robust_not["reference"]["accuracy"],
        "sigma_0_5_AND_reference_accuracy": robust_and["reference"]["accuracy"],
        "status": "REFERENCE_HARNESS_ONLY_NOT_ORIGINAL_NOTEBOOK_VALIDATION",
    }, indent=2))

if __name__ == "__main__":
    main()
