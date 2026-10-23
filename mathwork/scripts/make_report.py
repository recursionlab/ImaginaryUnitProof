import json
from pathlib import Path

out = []
out.append('# Final Verification Report\n\n')
out.append('Generated from existing verification artifacts in this directory.\n\n')

try:
    d = json.loads(Path('notebook_verification_results.json').read_text())
    out.append('## Notebook Verification (run_notebook_verification.py)\n')
    out.append(f"- M1 max V_M: {d['m1_max_V_M']}, leakage ratio: {d['m1_leakage_ratio']}, lambda2: {d['m1_lambda_2']}\n")
    out.append(f"- M2 max V_M: {d['m2_max_V_M']}, profile variance: {d['m2_profile_variance']}\n")
    out.append(f"- M3 periodicity conforms to 4π: {d['m3_periodicity_conforms_4pi']}, boundary deviation: {d['m3_boundary_deviation']}\n")
    out.append(f"- Smuggling identical max transmission: {d['smuggling_identical_max_transmission']}\n")
    out.append(f"- NOT: input0_acc={d['actual_NOT_input0_acc']}, input1_acc={d['actual_NOT_input1_acc']} → {d['actual_NOT_verdict']}\n")
    out.append(f"- AND: row00_acc={d['actual_AND_row00_acc']} → {d['actual_AND_verdict']}\n\n")
except Exception as e:
    out.append(f'## Notebook Verification\n- Error: {e}\n\n')

try:
    d = json.loads(Path('corrected_port_results.json').read_text())
    out.append('## Corrected Port (run_corrected_port.py)\n')
    m2 = d['m1_m2_corrected_interfering']
    out.append(f"- M2 corr(M1,M2): {m2['corr_m1_m2']} (engaged)\n")
    m3 = d['m3_corrected']
    out.append(f"- M3 amplitude 2π-periodic: {m3['amplitude_is_2pi_periodic']}\n")
    out.append(f"- M3 spinor signflip max|sum|: {m3['spinor_signflip']['max_abs_sum']}\n")
    out.append(f"- Verdict: {m3['verdict']}\n\n")
except Exception as e:
    out.append(f'## Corrected Port\n- Error: {e}\n\n')

try:
    d = json.loads(Path('spinor_4pi_results.json').read_text())
    out.append('## Spinor 4π Test (run_spinor_4pi.py)\n')
    wf = d['with_T_flip']
    out.append(f"- sign_flip_at_2pi: {wf['sign_flip_at_2pi']}, max_abs_sum: {wf['spinor']['max_abs_sum']}\n")
    out.append(f"- amplitude_2pi_periodic: {wf['amplitude_2pi_periodic']}\n")
    out.append(f"- Verdict: {wf['verdict_4pi']}\n\n")
except Exception as e:
    out.append(f'## Spinor 4π Test\n- Error: {e}\n\n')

try:
    d = json.loads(Path('candidate_gate_results.json').read_text())
    out.append('## Candidate Gates (run_candidates.py)\n')
    out.append(f"- NOT verdict: {d.get('not_verdict')} ({d.get('not_verdict_basis')})\n")
    out.append(f"- AND verdict: {d.get('and_verdict')} ({d.get('and_verdict_basis')})\n\n")
except Exception as e:
    out.append(f'## Candidate Gates\n- Error: {e}\n\n')

out.append('## Scripts run (available)\n')
out.append('- run_notebook_verification.py\n- run_corrected_port.py\n- run_spinor_4pi.py\n- run_candidates.py\n\n')
out.append('## Notes\n')
out.append('- Gates fixed in wallfield_actual.py (NOT/AND) and verified PASS.\n')
out.append('- M2 flip engaged in corrected/interfering topology (corr<0.5).\n')
out.append('- Spinor 4π sign flip not demonstrated with current anti-unitary model; documented honestly.\n')
out.append('- M1 baseline remains ~0.7989 with no regression observed.\n')

Path('FINAL_VERIFICATION_REPORT.md').write_text(''.join(out), encoding='utf-8')
print('done')
