# Confirmation Preregistration

No confirmation result may be reported until this document is filled with exact
case hashes and committed.

## Frozen Case Families

| Family | Inclusion rule | Parameter range | Freeze status |
| --- | --- | --- | --- |
| small parameter grid | finite IMS-RAS models not used in discovery; enumerated over capacity, WIP, AGV count, route mix, and rates | pending | not frozen |
| medium C5 rebuild | independently implemented M-D bidirectional case with DAG repair pair | pending | not frozen |
| adversarial boundary | attacks the strongest theorem assumptions | pending | not frozen |

## Preregistered Metrics

- theorem prediction correctness;
- minimality of `DeadlockCertificate`;
- exact deadlock probability;
- exact mean absorption time;
- conditioned deadlock path mass;
- independent DES confidence interval;
- supervisor throughput loss;
- supervisor makespan loss;
- supervisor WIP change;
- supervisor due-date-risk change;
- rare-event estimator variance and effective sample efficiency.

After freeze, every applicable supervisor-cost component listed above must be
reported. A component may be marked inapplicable only if the freeze entry records
the reason before any confirmation result is inspected.

## Preregistered Baselines

- static simple-cycle detector;
- state-dependent knot detector;
- Banker-style safety sequence;
- siphon-control baseline where Petri assumptions hold;
- exact maximally permissive supervisor on finite state space;
- delete-backflow route repair.

## Freeze Entry Template

```
freeze_id:
git_commit:
case_manifest_sha256:
case_json_sha256_by_id:
theory_manifest_sha256:
prediction_sheet_sha256:
experiment_script_manifest_sha256:
baseline_manifest_sha256:
runtime_lock_sha256:
random_stream_manifest_sha256:
metric_schema_sha256:
date_utc:
included_cases:
excluded_cases:
exclusion_reason:
metrics_locked:
baselines_locked:
metric_inapplicability_reasons:
owner:
```

Every hash field is required. If a field is genuinely not applicable, write
`N/A` plus a freeze-time reason in `metric_inapplicability_reasons` or a linked
freeze note; blank values are invalid.
