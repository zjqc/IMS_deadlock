# Confirmation Preregistration

No confirmation result may be reported until this document is filled with exact
case hashes and committed.

Current G4 stage: `B-PREREGISTRATION-CANDIDATE-PENDING-C-SEAL`.

The current local G4 bundle contains preregistered held-out inputs,
predictions, baseline applicability, metric applicability, random streams,
runtime lock, experiment-script manifest, theory manifest, exclusions, and
`case_manifest.json`. It does not contain `FREEZE_ENTRY.json`, so it is not a
C-sealed frozen bundle. The final implementation-lock reference for this stage is
`2a89fe1409d5000225e22499878454e964c01363`.

## Candidate Case Families

| Family | Inclusion rule | Parameter range | Freeze status |
| --- | --- | --- | --- |
| G4 CRP triad | S4PR agreement, unreachable structural/algebraic candidate, and BAS/AGV/AND outside-S4PR refusal | exact case JSON under `cases/confirmation/g4/cases/` | B preregistration candidate; pending C seal |
| G4 recorder target quantification | original target versus `L32/L33`-style output-only recorder count obligations | exact case JSON under `cases/confirmation/g4/cases/` | B preregistration candidate; pending C seal |
| G4 L30/B05 comparators | finite-capacity S3PR/ENS3PR sufficient resource baseline and small full-LTS monitor-cover comparator | exact case JSON under `cases/confirmation/g4/cases/` | B preregistration candidate; pending C seal |
| G4 IMS parameter grid | ten held-out bidirectional BAS grid cells | exact cell list in `G4_IMS_PARAMETER_GRID.json` and `predictions.json` | B preregistration candidate; pending C seal |
| G4 medium island rebuild | independently specified three-island BAS/AGV model | exact case JSON under `cases/confirmation/g4/cases/` | B preregistration candidate; pending C seal |
| G4 adversarial boundary | OR-of-AND, multi-capacity, AGV, and reservation snapshot boundary | exact case JSON under `cases/confirmation/g4/cases/` | B preregistration candidate; pending C seal |

## Candidate Case IDs

The B candidate contains these nine held-out case IDs:

- `G4_CRP_S4PR_AGREE`
- `G4_CRP_UNREACHABLE_CANDIDATE`
- `G4_CRP_OUTSIDE_S4PR`
- `G4_RECORDER_TARGET_QUANTIFICATION`
- `G4_L30_RESOURCE_BASELINE`
- `G4_B05_SUPERVISOR_COMPARATOR`
- `G4_IMS_PARAMETER_GRID`
- `G4_MEDIUM_ISLAND_REBUILD`
- `G4_ADVERSARIAL_BOUNDARY`

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

For the current G4 B candidate, all supervisor-cost components, conditioned
deadlock path mass, and rare-event efficiency are inapplicable for every G4
case. Exact CTMC probability and mean absorption time are applicable only to
`G4_IMS_PARAMETER_GRID` and `G4_MEDIUM_ISLAND_REBUILD`. DES confidence
intervals are applicable only to `G4_IMS_PARAMETER_GRID` and
`G4_MEDIUM_ISLAND_REBUILD`. These are freeze-time applicability decisions, not
post-result omissions.

After C seal, every applicable component listed above must be reported. A
component may be marked inapplicable only if the sealed entry records the reason
before any confirmation result is inspected.

## Preregistered Baselines

- static simple-cycle detector;
- state-dependent knot detector;
- Banker-style safety sequence;
- siphon-control baseline where Petri assumptions hold;
- exact maximally permissive supervisor on finite state space;
- delete-backflow route repair.
- `L30` finite-capacity S3PR/ENS3PR resource-configuration baseline, only as a
  sufficient/conservative comparator after S3PR applicability is proved;
- `L31` CRP/SBA overlap baseline, only with an explicit executable prefix and
  complete finite BFS/LTS oracle; SBA is a separately reported comparator;
- `L32/L33` recorder-transformation baseline, only with preservation-direction
  and fixed-target quantification reporting;
- `L34/L35` BA/SBA legal-firing-sequence filter for state-equation candidates;
- `B05` compressed maximally permissive supervisor comparator, only with full
  RG and MCPP/covering evidence.

## Freeze Entry Template

```
freeze_id:
implementation_commit:
preregistration_commit:
date_utc:
owner:
confirmation_results_inspected:
included_cases:
excluded_cases:
artifact_hashes:
  case_manifest_sha256:
  prediction_sheet_sha256:
  baseline_manifest_sha256:
  metric_schema_sha256:
  runtime_lock_sha256:
  random_stream_manifest_sha256:
  experiment_script_manifest_sha256:
  theory_manifest_sha256:
  exclusions_sha256:
case_json_sha256_by_id:
```

Every hash field and all nine case hashes are required; blank and `N/A` hashes
are invalid. Metric and baseline inapplicability is recorded in the separately
hashed manifests, not added after outcomes are inspected.

## Post-Freeze Execution Boundary

No G4 held-out scientific command may run until the C seal exists and the
no-result freeze checker reports `FROZEN` with zero validation errors. Before
that point, allowed validation is limited to structural parsing, schema checks,
canonical hashes, document checks, and tests that monkeypatch scientific
entrypoints.

After C seal, commands that cannot run in the locked runtime are execution
failures under the frozen protocol. They are not permission to edit case JSON,
predictions, baseline decisions, metric applicability, random streams, theory
hashes, or experiment-script hashes.
