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
- supervisor makespan or due-date risk cost;
- rare-event estimator variance and effective sample efficiency.

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
theory_manifest_sha256:
date_utc:
included_cases:
excluded_cases:
exclusion_reason:
metrics_locked:
baselines_locked:
owner:
```

