# G5 Claim Evidence Table

## Scope

This table maps each frozen G4 confirmation case to repository-relative rule
sources, raw evidence fields, and the status allowed after the G5 scoring
erratum. It does not introduce new claims beyond the frozen predictions and
metrics.

## Aggregate Status

| Aggregate | Value |
| --- | --- |
| Frozen cases | 9 |
| Original locked scorer counts | 4 `SUPPORTED`, 3 `FALSIFIED`, 2 `INCONCLUSIVE` |
| Rule-audit theorem counts | 6 `SUPPORTED`, 1 `FALSIFIED`, 2 `INCONCLUSIVE` |
| Exact primary/repro matches | 9/9 |
| Paper gate | `FAIL` |

## Claim-Evidence Mapping

| Case | Frozen rule source | Raw evidence fields | Rule-audit theorem status | Metric / boundary status |
| --- | --- | --- | --- | --- |
| `G4_ADVERSARIAL_BOUNDARY` | `cases/confirmation/g4/predictions.json`; `cases/confirmation/g4/metrics_schema.json` | `classification`; `analysis.certificate`; `analysis.petri_bridge`; `observations.frozen_request_transition_enabled` | `SUPPORTED` | `certificate_minimality=FAIL`; original scorer marked `FALSIFIED` for this metric failure |
| `G4_B05_SUPERVISOR_COMPARATOR` | `cases/confirmation/g4/predictions.json`; `cases/confirmation/g4/metrics_schema.json` | `classification` | `SUPPORTED` | exact-only comparator; performance metrics inapplicable |
| `G4_CRP_OUTSIDE_S4PR` | `cases/confirmation/g4/predictions.json`; `cases/confirmation/g4/metrics_schema.json` | `classification`; `evidence_profile_audit.classification`; `outside_scope_boundary.analysis.certificate`; `outside_scope_boundary.analysis.petri_bridge` | `SUPPORTED` | `certificate_minimality=FAIL`; original scorer marked `FALSIFIED` for this metric failure |
| `G4_CRP_S4PR_AGREE` | `cases/confirmation/g4/predictions.json`; `cases/confirmation/g4/metrics_schema.json` | `classification`; `evidence_profile_audit.classification`; `partial_deadlock_bridge.agrees`; `partial_deadlock_bridge.certificate_available`; `partial_deadlock_bridge.certificate` | `FALSIFIED` | bridge disagreement retained; no certificate payload |
| `G4_CRP_UNREACHABLE_CANDIDATE` | `cases/confirmation/g4/predictions.json`; `cases/confirmation/g4/metrics_schema.json` | `classification`; `evidence_profile_audit.classification` | `SUPPORTED` | exact nonreachability row; certificate and stochastic metrics inapplicable |
| `G4_IMS_PARAMETER_GRID` | `cases/confirmation/g4/predictions.json`; `cases/confirmation/g4/metrics_schema.json`; `cases/confirmation/g4/runtime_lock.json` | `stderr.txt`; `record.json.exit_code`; `record.json.stdout_canonical_json_sha256` | `INCONCLUSIVE` | nonzero exit; `ValueError: state 's5' must have reachable absorbing transition`; no canonical JSON payload |
| `G4_L30_RESOURCE_BASELINE` | `cases/confirmation/g4/predictions.json`; `cases/confirmation/g4/metrics_schema.json` | `classification` | `SUPPORTED` | exact sufficient-inequality comparator; no IMS necessity or probability claim |
| `G4_MEDIUM_ISLAND_REBUILD` | `cases/confirmation/g4/predictions.json`; `cases/confirmation/g4/metrics_schema.json`; `cases/confirmation/g4/runtime_lock.json` | `stderr.txt`; `record.json.exit_code`; `record.json.stdout_canonical_json_sha256` | `INCONCLUSIVE` | nonzero exit; `ValueError: state 's79' must have reachable absorbing transition`; no canonical JSON payload |
| `G4_RECORDER_TARGET_QUANTIFICATION` | `cases/confirmation/g4/predictions.json`; `cases/confirmation/g4/metrics_schema.json` | `classification` | `SUPPORTED` | exact fixed-target quantification; stochastic metrics inapplicable |

## Allowed Manuscript Claims

Allowed after the erratum:

- report that all 9/9 primary/repro capture pairs matched exactly;
- report the original locked scorer counts as 4/3/2 with preserved hashes;
- report the rule-audit theorem counts as 6/1/2 only with the erratum attached;
- report `G4_ADVERSARIAL_BOUNDARY` and `G4_CRP_OUTSIDE_S4PR` theorem predictions
  as supported while separately reporting `certificate_minimality=FAIL`;
- report `G4_CRP_S4PR_AGREE` as falsified;
- report `G4_MEDIUM_ISLAND_REBUILD` and `G4_IMS_PARAMETER_GRID` as inconclusive
  due to the exact `s79` and `s5` CTMC validation failures.

Not allowed:

- claiming G5 paper-gate pass;
- dropping the original 4/3/2 scorer output;
- using the 6/1/2 rule-audit counts without the scorer erratum;
- treating certificate minimality failures as fixed;
- rerunning, retuning, or changing sealed G4 inputs to repair the two
  inconclusive stochastic cases.

## Successor Work

The next scorer/report schema must emit separate fields for theorem prediction
correctness and metric statuses. It must regenerate compact scored evidence
from the unchanged raw captures and retain all negative, failed, and
inconclusive rows.
