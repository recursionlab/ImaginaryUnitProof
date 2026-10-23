from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from candidate_formulas import and_phase_candidate_m1, and_phase_candidate_m2, not_phase_candidate
from gate_contract_audit import NOISE_SIGMAS, SEEDS, TRIALS_PER_ROW_PER_SEED, confusion, encode_bit

OUT = Path(__file__).resolve().parent


def _not_inputs(seed: int, sigma: float):
    rng = np.random.default_rng(seed + int(round(sigma * 10000)))
    balanced = np.repeat(np.array([0, 1], dtype=np.int8), TRIALS_PER_ROW_PER_SEED)
    rng.shuffle(balanced)
    phi_in = encode_bit(balanced) + rng.normal(0.0, sigma, size=balanced.size)
    out_noise = rng.normal(0.0, sigma, size=balanced.size)
    actual = (1 - balanced).astype(np.int8)
    return balanced, phi_in, out_noise, actual


def run_not_candidate(sigma: float) -> dict:
    actual_blocks, pred_blocks, input_blocks = [], [], []
    for seed in SEEDS:
        balanced, phi_in, out_noise, actual = _not_inputs(seed, sigma)
        pred = not_phase_candidate(phi_in, out_noise)
        actual_blocks.append(actual)
        pred_blocks.append(pred)
        input_blocks.append(balanced)
    actual = np.concatenate(actual_blocks)
    pred = np.concatenate(pred_blocks)
    inputs = np.concatenate(input_blocks)
    per_input = {}
    for bit in (0, 1):
        mask = inputs == bit
        per_input[str(bit)] = {
            "n": int(mask.sum()),
            "candidate_accuracy": float(np.mean(pred[mask] == actual[mask])),
        }
    return {
        "sigma_rad": sigma,
        "n": int(actual.size),
        "candidate_NOT": confusion(actual, pred),
        "per_input": per_input,
    }


def run_and_candidate(sigma: float) -> dict:
    truth_all, m1_all, m2_all = [], [], []
    row_results = {}
    for a_bit, b_bit in ((0, 0), (0, 1), (1, 0), (1, 1)):
        truth_blocks, m1_blocks, m2_blocks = [], [], []
        for seed in SEEDS:
            rng = np.random.default_rng(seed + 1000000 + int(round(sigma * 10000)) + a_bit * 101 + b_bit * 313)
            n = TRIALS_PER_ROW_PER_SEED
            phi_a = encode_bit(np.full(n, a_bit)) + rng.normal(0.0, sigma, size=n)
            phi_b = encode_bit(np.full(n, b_bit)) + rng.normal(0.0, sigma, size=n)
            on1 = rng.normal(0.0, sigma, size=n)
            on2 = rng.normal(0.0, sigma, size=n)
            m1 = and_phase_candidate_m1(phi_a, phi_b, on1)
            m2 = and_phase_candidate_m2(phi_a, phi_b, on2)
            truth = np.full(n, a_bit & b_bit, dtype=np.int8)
            truth_blocks.append(truth); m1_blocks.append(m1); m2_blocks.append(m2)
        truth = np.concatenate(truth_blocks)
        c1 = np.concatenate(m1_blocks)
        c2 = np.concatenate(m2_blocks)
        row_results[f"{a_bit}{b_bit}"] = {
            "n": int(truth.size),
            "truth_output": int(a_bit & b_bit),
            "candidate_M1_accuracy": float(np.mean(c1 == truth)),
            "candidate_M2_accuracy": float(np.mean(c2 == truth)),
            "candidate_M1_confusion": confusion(truth, c1),
            "candidate_M2_confusion": confusion(truth, c2),
        }
        truth_all.append(truth); m1_all.append(c1); m2_all.append(c2)
    actual = np.concatenate(truth_all)
    m1 = np.concatenate(m1_all)
    m2 = np.concatenate(m2_all)
    return {
        "sigma_rad": sigma,
        "n": int(actual.size),
        "truth_table_rows": row_results,
        "candidate_M1": confusion(actual, m1),
        "candidate_M2": confusion(actual, m2),
        "row_order": ["00", "01", "10", "11"],
    }


def make_plot(not_results, and_results) -> Path:
    sigmas = [r["sigma_rad"] for r in not_results]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    axes[0].plot(sigmas, [r["candidate_NOT"]["accuracy"] for r in not_results], marker="o", label="NOT candidate (always HIGH)")
    axes[0].axhline(0.5, color="r", linestyle=":", alpha=0.5, label="chance = 0.5")
    axes[0].set_title("NOT candidate: no inversion")
    axes[0].set_xlabel("phase-noise σ (rad)"); axes[0].set_ylabel("accuracy")
    axes[0].set_ylim(-0.03, 1.03); axes[0].grid(True, alpha=.25); axes[0].legend()
    axes[1].plot(sigmas, [r["candidate_M1"]["accuracy"] for r in and_results], marker="o", label="AND candidate M1 (cos diff)")
    axes[1].plot(sigmas, [r["candidate_M2"]["accuracy"] for r in and_results], marker="s", label="AND candidate M2 (cos sum)")
    axes[1].axhline(0.75, color="r", linestyle=":", alpha=0.5, label="XNOR ceiling = 0.75")
    axes[1].set_title("AND candidates: both reduce to XNOR")
    axes[1].set_xlabel("phase-noise σ (rad)"); axes[1].set_ylabel("accuracy")
    axes[1].set_ylim(-0.03, 1.03); axes[1].grid(True, alpha=.25); axes[1].legend()
    fig.suptitle("Candidate formulas vs frozen gate contract (candidates are the defect-class formulas)")
    fig.tight_layout()
    path = OUT / "candidate_gate_vs_reference.png"
    fig.savefig(path, dpi=170, bbox_inches="tight"); plt.close(fig)
    return path


def per_row(and_result, variant: str, row: str) -> dict:
    r = and_result["truth_table_rows"][row]
    conf = r[f"{variant}_confusion"]
    wrong = conf["FP"] + conf["FN"]
    return {
        "truth_output": r["truth_output"],
        "accuracy": r[f"{variant}_accuracy"],
        "confusion": conf["matrix"],
        "verdict": "PASS" if wrong == 0 else "FAIL",
    }


def main() -> None:
    not_results = [run_not_candidate(float(s)) for s in NOISE_SIGMAS]
    and_results = [run_and_candidate(float(s)) for s in NOISE_SIGMAS]
    result = {
        "title": "Candidate phase-gate formulas vs frozen gate contract",
        "status": "CANDIDATE_TESTING — candidates are the defect-class formulas, not the Boolean reference",
        "disclaimer": (
            "not_phase_candidate reproduces the documented failure signature (both inputs HIGH). "
            "and_phase_candidate_* reproduce the wave-logic bond gate W=w*cos(Delta_phi) with HIGH iff W>=0, "
            "which algebraically reduces to XNOR for the 0/pi encoding."
        ),
        "candidates": {
            "NOT_phase_candidate": "always HIGH (failure signature from scoring_verdict transcript)",
            "AND_phase_candidate_M1": "HIGH iff cos(phi_a - phi_b) >= 0  => XNOR truth table",
            "AND_phase_candidate_M2": "HIGH iff cos(phi_a + phi_b) >= 0  => XNOR truth table (00,11 high; 01,10 low)",
        },
        "NOT": not_results,
        "AND": and_results,
    }
    json_path = OUT / "candidate_gate_results.json"
    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    plot_path = make_plot(not_results, and_results)

    z0_not = not_results[0]
    z0_and = and_results[0]
    s05_not = not_results[3]
    s05_and = and_results[3]
    not_per_input = z0_not["per_input"]
    rows_lines = "\n".join(
        f"  - {row}: truth={per_row(z0_and,'candidate_M1',row)['truth_output']} "
        f"candidate_accuracy={per_row(z0_and,'candidate_M1',row)['accuracy']:.3f} "
        f"confusion={per_row(z0_and,'candidate_M1',row)['confusion']} "
        f"verdict={per_row(z0_and,'candidate_M1',row)['verdict']}"
        for row in z0_and["row_order"]
    )
    report = f'''# Candidate gate-contract test — verdicts

## Boundary

The truth tables, seeds, trial counts, noise sweep, and `[[TN,FP],[FN,TP]]` convention are
**imported unchanged** from `gate_contract_audit.py` and are frozen. Only the candidate model
bodies are substituted; the target truth table and acceptance criteria never move.

## NOT candidate (always-HIGH failure signature, transcribed from handoff)

- Zero-noise accuracy: **{z0_not['candidate_NOT']['accuracy']:.3f}**; confusion {z0_not['candidate_NOT']['matrix']}.
- Per-input (zero noise): input 0 -> {not_per_input['0']['candidate_accuracy']:.3f}, input 1 -> {not_per_input['1']['candidate_accuracy']:.3f}.
- At σ=0.50 rad accuracy: **{s05_not['candidate_NOT']['accuracy']:.3f}**.
- Verdict: **FAIL** — true NOT inverts both rows; this candidate maps both inputs to HIGH.

## AND candidates (bond gate `HIGH iff W>=0`)

Both M1 (`cos(phi_a-phi_b)`) and M2 (`cos(phi_a+phi_b)`) decide HIGH when the bond is non-negative.
Under the `0->0, 1->pi` encoding this is the XNOR truth table (`00->1, 01->0, 10->0, 11->1`),
disagreeing with AND only on row `00`.

- Zero-noise M1 accuracy: **{z0_and['candidate_M1']['accuracy']:.3f}**; M2 accuracy: **{z0_and['candidate_M2']['accuracy']:.3f}**.
- Per-row (zero noise):
{rows_lines}
- At σ=0.50 rad: M1 **{s05_and['candidate_M1']['accuracy']:.3f}**, M2 **{s05_and['candidate_M2']['accuracy']:.3f}**.
- Aggregate accuracy is ~0.75 but **row `00` is always wrong** — the "aggregate accuracy conceals a wrong truth-table row" defect the harness was built to expose.
- Verdict: **FAIL** — M1 and M2 bond gates implement XNOR, not AND.

## Why this matters for the wall

The reference NOT (`phi_in + pi`) and reference AND (decode both, apply Boolean table) pass.
The wave-logic bond candidates fail. The original M1/M2 verdicts report identical
`max_transmitted_V_M = 0.7989` and `leakage_ratio = 0.0` — those numbers are **not** produced
by these candidates, indicating the original verdicts came from a different code path never wired
into this contract. That mismatch must be resolved before any wall certification.
'''
    (OUT / "candidate_gate_contract_report.md").write_text(report, encoding="utf-8")
    print(json.dumps({
        "report": str(OUT / "candidate_gate_contract_report.md"),
        "results": str(json_path),
        "plot": str(plot_path),
        "zero_noise_NOT_candidate_accuracy": z0_not["candidate_NOT"]["accuracy"],
        "zero_noise_AND_M1_candidate_accuracy": z0_and["candidate_M1"]["accuracy"],
        "zero_noise_AND_M2_candidate_accuracy": z0_and["candidate_M2"]["accuracy"],
        "sigma_0_5_NOT_candidate_accuracy": s05_not["candidate_NOT"]["accuracy"],
        "sigma_0_5_AND_M1_candidate_accuracy": s05_and["candidate_M1"]["accuracy"],
        "not_verdict": "FAIL",
        "and_verdict": "FAIL",
        "not_verdict_basis": "both NOT inputs produce HIGH; no inversion",
        "and_verdict_basis": "M1 and M2 bond gates reduce to XNOR (row 00 wrong)",
    }, indent=2))


if __name__ == "__main__":
    main()
