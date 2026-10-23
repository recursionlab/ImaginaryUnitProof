"""Round 8 — Ruthless self-audit of cell-27 gate truth tables at sigma=0, multi-seed.

Uses notebook-exact simulate_noisy_not_gate / simulate_noisy_and_gate from
wallfield_actual.py (the documented port of notebook cell 27), with an explicit
5-seed override pulled from gate_contract_audit.SEEDS.
"""
from __future__ import annotations
import math
import numpy as np

from wallfield_actual import (
    simulate_noisy_not_gate,
    simulate_noisy_and_gate,
    GATE_DECISION_THRESHOLD,
)
from gate_contract_audit import SEEDS, TRIALS_PER_ROW_PER_SEED

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SIGMA = 0.0
# Override to exactly 5 explicit seeds (same values as gate_contract_audit.SEEDS)
FIVE_SEEDS = list(SEEDS[:5])
assert len(FIVE_SEEDS) == 5, f"Expected 5 seeds, got {len(FIVE_SEEDS)}"

# Phase encoding: bit 0 -> 0 rad, bit 1 -> pi rad
BIT_TO_PHASE = {0: 0.0, 1: math.pi}

# Truth tables
NOT_TRUTH = {0: 1, 1: 0}          # NOT(0)=1, NOT(1)=0
AND_TRUTH = {(0,0): 0, (0,1): 0, (1,0): 0, (1,1): 1}

def amp_to_bit(amp: float) -> int:
    return int(amp >= GATE_DECISION_THRESHOLD)


def confusion(actual_bits, predicted_bits):
    a = np.asarray(actual_bits, dtype=int)
    p = np.asarray(predicted_bits, dtype=int)
    tn = int(np.sum((a == 0) & (p == 0)))
    fp = int(np.sum((a == 0) & (p == 1)))
    fn = int(np.sum((a == 1) & (p == 0)))
    tp = int(np.sum((a == 1) & (p == 1)))
    total = tn + fp + fn + tp
    acc = (tn + tp) / total if total else 0.0
    return tn, fp, fn, tp, acc


def run_not_row(input_bit: int) -> dict:
    """Run NOT gate for a given logical input bit across all 5 seeds."""
    phase = BIT_TO_PHASE[input_bit]
    expected = NOT_TRUTH[input_bit]
    all_actual = []
    all_predicted = []
    amplitudes = []
    for seed in FIVE_SEEDS:
        rng = np.random.default_rng(seed)
        for _ in range(TRIALS_PER_ROW_PER_SEED):
            amp = simulate_noisy_not_gate(phase, SIGMA, rng=rng)
            bit = amp_to_bit(amp)
            all_actual.append(expected)
            all_predicted.append(bit)
            amplitudes.append(amp)
    tn, fp, fn, tp, acc = confusion(all_actual, all_predicted)
    amp_arr = np.array(amplitudes)
    return {
        "input_bit": input_bit,
        "input_phase_rad": phase,
        "expected_output": expected,
        "n": len(all_actual),
        "TP": tp, "FP": fp, "TN": tn, "FN": fn,
        "accuracy": acc,
        "amplitude_mean": float(np.mean(amp_arr)),
        "amplitude_min": float(np.min(amp_arr)),
        "amplitude_max": float(np.max(amp_arr)),
        "correct": acc == 1.0,
    }


def run_and_row(a_bit: int, b_bit: int) -> dict:
    """Run AND gate for a given pair of logical input bits across all 5 seeds."""
    phase_a = BIT_TO_PHASE[a_bit]
    phase_b = BIT_TO_PHASE[b_bit]
    expected = AND_TRUTH[(a_bit, b_bit)]
    all_actual = []
    all_predicted = []
    amplitudes = []
    for seed in FIVE_SEEDS:
        rng = np.random.default_rng(seed)
        for _ in range(TRIALS_PER_ROW_PER_SEED):
            amp = simulate_noisy_and_gate(phase_a, phase_b, SIGMA, rng=rng)
            bit = amp_to_bit(amp)
            all_actual.append(expected)
            all_predicted.append(bit)
            amplitudes.append(amp)
    tn, fp, fn, tp, acc = confusion(all_actual, all_predicted)
    amp_arr = np.array(amplitudes)
    return {
        "input_pair": f"{a_bit}{b_bit}",
        "phase_a_rad": phase_a,
        "phase_b_rad": phase_b,
        "delta_phi_rad": float(phase_a - phase_b),
        "expected_output": expected,
        "n": len(all_actual),
        "TP": tp, "FP": fp, "TN": tn, "FN": fn,
        "accuracy": acc,
        "amplitude_mean": float(np.mean(amp_arr)),
        "amplitude_min": float(np.min(amp_arr)),
        "amplitude_max": float(np.max(amp_arr)),
        "correct": acc == 1.0,
    }


def main() -> dict:
    print("=" * 78)
    print("ROUND 8 — Cell-27 gate truth-table per-row audit (sigma=0.0, 5 seeds)")
    print("=" * 78)
    print(f"SEEDS = {FIVE_SEEDS}")
    print(f"SIGMA = {SIGMA} rad  |  TRIALS_PER_ROW_PER_SEED = {TRIALS_PER_ROW_PER_SEED}")
    print(f"GATE_DECISION_THRESHOLD = {GATE_DECISION_THRESHOLD}")
    print()

    # --- NOT gate audit ---
    print("--- NOT GATE (expected: NOT(0)=1 HIGH, NOT(1)=0 LOW) ---")
    not_results = {}
    for bit in (0, 1):
        r = run_not_row(bit)
        not_results[str(bit)] = r
        print(f"  NOT row {r['input_bit']}:")
        print(f"    input_phase  = {r['input_phase_rad']:.4f} rad ({'0' if r['input_phase_rad']==0 else 'pi'})")
        print(f"    expected_out = {r['expected_output']}")
        print(f"    TP={r['TP']} FP={r['FP']} TN={r['TN']} FN={r['FN']} n={r['n']}")
        print(f"    accuracy     = {r['accuracy']:.4f}")
        print(f"    amplitude    = {r['amplitude_mean']:.6f}  [min={r['amplitude_min']:.6f}, max={r['amplitude_max']:.6f}]")
        print(f"    CORRECT: {r['correct']}")
        print()

    # --- AND gate audit ---
    print("--- AND GATE (expected truth table: 00->0, 01->0, 10->0, 11->1) ---")
    and_results = {}
    for a_bit, b_bit in ((0,0), (0,1), (1,0), (1,1)):
        r = run_and_row(a_bit, b_bit)
        and_results[r["input_pair"]] = r
        print(f"  AND row {r['input_pair']}:")
        print(f"    phase_a={r['phase_a_rad']:.4f} rad, phase_b={r['phase_b_rad']:.4f} rad")
        print(f"    delta_phi = {r['delta_phi_rad']:.4f} rad")
        print(f"    expected_out = {r['expected_output']}")
        print(f"    TP={r['TP']} FP={r['FP']} TN={r['TN']} FN={r['FN']} n={r['n']}")
        print(f"    accuracy     = {r['accuracy']:.4f}")
        print(f"    amplitude    = {r['amplitude_mean']:.6f}  [min={r['amplitude_min']:.6f}, max={r['amplitude_max']:.6f}]")
        print(f"    CORRECT: {r['correct']}")
        print()

    # --- Summary of broken rows ---
    print("=" * 78)
    print("BROKEN ROWS SUMMARY")
    print("=" * 78)
    broken = []
    for bit, r in not_results.items():
        if not r["correct"]:
            broken.append(("NOT", r["input_bit"], r))
            print(f"  BROKEN: NOT row {bit} — amplitude={r['amplitude_mean']:.6f} "
                  f"(expected {'LOW' if r['expected_output']==0 else 'HIGH'}), "
                  f"acc={r['accuracy']:.4f}")
    for pair, r in and_results.items():
        if not r["correct"]:
            broken.append(("AND", r["input_pair"], r))
            print(f"  BROKEN: AND row {pair} — amplitude={r['amplitude_mean']:.6f} "
                  f"(expected {'LOW' if r['expected_output']==0 else 'HIGH'}), "
                  f"acc={r['accuracy']:.4f}")
    if not broken:
        print("  (none)")
    print()

    # --- Algebraic proof: AND candidate is XNOR ---
    print("=" * 78)
    print("ALGEBRAIC PROOF: AND candidate amplitude |cos((phi_a-phi_b)/2)| is XNOR")
    print("=" * 78)
    print()
    print("Candidate formula (wallfield_actual.simulate_noisy_and_gate, sigma=0):")
    print("  amplitude = |cos((phi_a - phi_b) / 2)|")
    print()
    print("Encoding: bit 0 -> phase 0, bit 1 -> phase pi  =>  phi = pi * bit")
    print("  =>  delta_phi = phi_a - phi_b = pi * (a - b)")
    print("  =>  amplitude = |cos(pi * (a - b) / 2)|")
    print()
    print("Evaluate for all four (a, b) in {0,1}^2:")
    print(f"  {'(a,b)':>8} | {'a-b':>4} | {'delta_phi/pi':>13} | {'cos(delta/2)':>15} | {'amp':>6} | {'bit':>4} | {'AND':>4} | {'XNOR':>4}")
    print("  " + "-" * 80)
    for a in (0, 1):
        for b in (0, 1):
            d = a - b
            delta_phi = math.pi * d
            cos_val = math.cos(delta_phi / 2.0)
            amp = abs(cos_val)
            bit = 1 if amp >= GATE_DECISION_THRESHOLD else 0
            and_out = a & b
            xnor_out = 1 - (a ^ b)
            print(f"  {a}{b:>7} | {d:>4} | {d:>13} | {cos_val:>15.6f} | {amp:>6.3f} | {bit:>4} | {and_out:>4} | {xnor_out:>4}")
    print()
    print("Key observations:")
    print("  1. Rows 00 and 11 both give delta_phi=0 => amplitude=|cos(0)|=1 => bit HIGH.")
    print("     But AND requires 00->LOW(0) and 11->HIGH(1). The candidate gives HIGH for BOTH.")
    print("  2. Row 00: candidate=HIGH(1), AND=LOW(0)   => FP (false positive).")
    print("  3. Rows 01 and 10 both give |delta_phi|=pi => amplitude=|cos(pi/2)|=0 => bit LOW.")
    print("     AND requires both LOW(0) — candidate matches on these rows (TN).")
    print("  4. Row 11: candidate=HIGH(1), AND=HIGH(1)  => TP (correct).")
    print()
    print("WHY THIS IS FUNDAMENTAL (not a fixable bug):")
    print("  - cos(x) is an EVEN function: cos(-x) = cos(x).")
    print("  - Therefore |cos((phi_a-phi_b)/2)| depends only on |phi_a - phi_b|,")
    print("    which is INVARIANT under swapping a<->b and under the simultaneous")
    print("    flip a,b -> 1-a,1-b (both negate phi_a and phi_b, leaving the difference unchanged).")
    print("  - Concretely: (a,b)=(0,0) and (a,b)=(1,1) both yield delta_phi=0,")
    print("    so the amplitude is IDENTICAL (1.0) for both. AND requires different")
    print("    outputs for these two rows (0 vs 1). No threshold or noise can separate")
    print("    them because the raw amplitude is provably equal at zero noise.")
    print("  - The candidate truth table is 1,0,0,1 = XNOR (equivalence), not 0,0,0,1 = AND.")
    print("  - This is a structural/logic-type mismatch in the formula's zero-noise limit,")
    print("    independent of noise model, seed, or threshold. It cannot be patched by tuning.")
    print()

    return {
        "sigma": SIGMA,
        "seeds": FIVE_SEEDS,
        "not_results": not_results,
        "and_results": and_results,
        "broken_rows": [(t, p, r) for t, p, r in broken],
    }


if __name__ == "__main__":
    results = main()
