from __future__ import annotations

import numpy as np

from gate_contract_audit import decode_phase, encode_bit

CANDIDATE_DISCLAIMER = (
    "These functions are transcribed from the handoff equations in audit_results.json "
    "(M1 weight rule w*cos(phi_s - phi_t); M2 weight rule w*cos(phi_s + phi_t)) and the "
    "observed failure signature in scoring_verdict.json / the gate-contract transcript. "
    "They are the candidates to be tested against the FROZEN contract in gate_contract_audit.py. "
    "The truth tables, seeds, noise sweep, and decode rule are imported unchanged."
)


def m1_weight(phi_source: np.ndarray, phi_target: np.ndarray) -> np.ndarray:
    return np.cos(np.asarray(phi_source) - np.asarray(phi_target))


def m2_weight(phi_source: np.ndarray, phi_target: np.ndarray) -> np.ndarray:
    return np.cos(np.asarray(phi_source) + np.asarray(phi_target))


def not_phase_candidate(phi_in: np.ndarray, output_noise: np.ndarray) -> np.ndarray:
    del output_noise
    return np.ones_like(np.asarray(phi_in), dtype=np.int8)


def _bond_and(phi_a: np.ndarray, phi_b: np.ndarray, weight_fn, output_noise: np.ndarray) -> np.ndarray:
    w = weight_fn(np.asarray(phi_a), np.asarray(phi_b))
    high_when_aligned = (w >= 0.0).astype(np.int8)
    predicted = encode_bit(high_when_aligned)
    return decode_phase(predicted + np.asarray(output_noise))


def and_phase_candidate_m1(phi_a: np.ndarray, phi_b: np.ndarray, output_noise: np.ndarray) -> np.ndarray:
    return _bond_and(phi_a, phi_b, m1_weight, output_noise)


def and_phase_candidate_m2(phi_a: np.ndarray, phi_b: np.ndarray, output_noise: np.ndarray) -> np.ndarray:
    return _bond_and(phi_a, phi_b, m2_weight, output_noise)


def and_truth_table_reference(phi_a: np.ndarray, phi_b: np.ndarray, output_noise: np.ndarray) -> np.ndarray:
    from gate_contract_audit import and_truth_table_reference as _ref

    return _ref(phi_a, phi_b, output_noise)


def not_phase_reference(phi_in: np.ndarray, output_noise: np.ndarray) -> np.ndarray:
    from gate_contract_audit import not_phase_reference as _ref

    return _ref(phi_in, output_noise)
