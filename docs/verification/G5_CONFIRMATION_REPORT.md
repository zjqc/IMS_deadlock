# G5 Confirmation Report

## Scope

This report covers the nine frozen G4 confirmation cases under freeze
`G4-FREEZE-C-20260730T051210Z`. It records the supplied G5 evidence only:
`G5_RESULT_SUMMARY.json`, `G5_RAW_HASH_MANIFEST.json`, the raw capture archive,
`evidence/g5/G5_EXECUTION_LOCK.json`, and the frozen rule sources under
`cases/confirmation/g4/`.

No case, prediction, metric, stream, command, timeout, raw output, sealed input,
rerun, or tuning parameter was changed for this report.

## Locked Inputs

| Item | Value |
| --- | --- |
| G5-A tooling commit | `b5e5dc0494b23a54c78c420bbca50a3639de8bff` |
| G5-B execution lock commit | `8aa752804b885b79e5371c98e7961087c540f2a8` |
| Post-execution evidence commit | `ff281481068a2325cb0bde00e85fd7b753ba854a` (verified on the authoritative Dell G5 worktree) |
| Original scorer hash | `10fe19c835b958cf3ccdf8116a527eab159543ba642590489584230875121a48` |
| Original summary hash | `db36cce977015890618c93b8872a33d70ff158c4f69ad5277fc1eaee33f29815` |
| Raw manifest hash | `c1940b5f421d5a22621d36a69fb055672d809277ccb8739d7ca2304b81397cf4` |
| Prediction sheet hash | `644bc94a188b1de06fa6d841b5a50a293c831943a8f51bafcd46ebedb5a2f3bd` |
| Metric schema hash | `5ce58b7ffec2fe09166de8d41b69371990bddebae724f47cf350feb7fe41aeb6` |
| Runtime | `D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe`, Python 3.13.9 |

## Original Locked Scorer Result

The original locked scorer result is preserved as generated:

| Count type | Result |
| --- | --- |
| Case count | 9 |
| Execution status | 7 `COMPLETED`, 2 `NONZERO_EXIT` |
| Scientific status | 4 `SUPPORTED`, 3 `FALSIFIED`, 2 `INCONCLUSIVE` |
| Overall `supported` flag | `false` |

The original generated files are identified by:

- `evidence/g5/G5_RESULT_SUMMARY.json`:
  `db36cce977015890618c93b8872a33d70ff158c4f69ad5277fc1eaee33f29815`
- `evidence/g5/G5_RAW_HASH_MANIFEST.json`:
  `c1940b5f421d5a22621d36a69fb055672d809277ccb8739d7ca2304b81397cf4`

## Rule-Audit Erratum

An independent rule audit found a category error in the locked scorer. The
scorer treated `certificate_minimality` metric failures as theorem-prediction
falsifiers for two cases whose frozen prediction rules do not require
certificate minimality.

Corrected theorem-prediction counts for rule-audit purposes are:

| Theorem prediction status | Count |
| --- | ---: |
| `SUPPORTED` | 6 |
| `FALSIFIED` | 1 |
| `INCONCLUSIVE` | 2 |

This correction does not modify the raw execution records or the original
locked scorer summary. It separates theorem prediction correctness from the
`certificate_minimality` metric.

## Case Outcomes

| Case | Execution | Original scorer status | Rule-audit theorem status | Metric / failure retained |
| --- | --- | --- | --- | --- |
| `G4_ADVERSARIAL_BOUNDARY` | `COMPLETED` | `FALSIFIED` | `SUPPORTED` | `certificate_minimality=FAIL`; raw `analysis.certificate.certificate.is_minimal=false` |
| `G4_B05_SUPERVISOR_COMPARATOR` | `COMPLETED` | `SUPPORTED` | `SUPPORTED` | none |
| `G4_CRP_OUTSIDE_S4PR` | `COMPLETED` | `FALSIFIED` | `SUPPORTED` | `certificate_minimality=FAIL`; raw `outside_scope_boundary.analysis.certificate.certificate.is_minimal=false` |
| `G4_CRP_S4PR_AGREE` | `COMPLETED` | `FALSIFIED` | `FALSIFIED` | bridge disagreement; certificate unavailable; resource equality failed |
| `G4_CRP_UNREACHABLE_CANDIDATE` | `COMPLETED` | `SUPPORTED` | `SUPPORTED` | none |
| `G4_IMS_PARAMETER_GRID` | `NONZERO_EXIT` | `INCONCLUSIVE` | `INCONCLUSIVE` | CTMC validation error: state `s5` must have reachable absorbing transition |
| `G4_L30_RESOURCE_BASELINE` | `COMPLETED` | `SUPPORTED` | `SUPPORTED` | none |
| `G4_MEDIUM_ISLAND_REBUILD` | `NONZERO_EXIT` | `INCONCLUSIVE` | `INCONCLUSIVE` | CTMC validation error: state `s79` must have reachable absorbing transition |
| `G4_RECORDER_TARGET_QUANTIFICATION` | `COMPLETED` | `SUPPORTED` | `SUPPORTED` | none |

## Gate Verdict

`G5 paper gate = FAIL`.

Reasons:

1. The original locked scorer result remains 4 `SUPPORTED`, 3 `FALSIFIED`, and
   2 `INCONCLUSIVE`.
2. The rule-audit correction still leaves one theorem falsification
   (`G4_CRP_S4PR_AGREE`) and two inconclusive stochastic cases.
3. The scorer category error requires a successor scorer/report schema before
   the evidence can be used as a paper-pass table.

## Successor Requirement

A successor pass must separate:

- `theorem_prediction_correctness`;
- `certificate_minimality`;
- other metric statuses.

The successor pass must regenerate compact scored evidence from the unchanged
raw captures. It must not rerun cases, retune parameters, edit sealed G4 inputs,
or drop negative and inconclusive rows.
