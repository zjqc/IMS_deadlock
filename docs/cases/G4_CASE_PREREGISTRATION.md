# G4 Literature-Informed Case Preregistration

Status: `B-PREREGISTRATION-CANDIDATE-PENDING-C-SEAL`.

This document records the B-stage G4 preregistration candidate after the
seven-paper audit and final implementation lock
`2a89fe1409d5000225e22499878454e964c01363`. The held-out JSON inputs,
predictions, baseline applicability, metric applicability, random streams,
runtime lock, script manifest, theory manifest, and exclusions currently live
under `cases/confirmation/g4/`.

This is not a C seal. `case_manifest.json` is present, but
`FREEZE_ENTRY.json` is not present in the current local bundle, so G4 remains
pending C seal and no held-out scientific backend may be executed or reported
from these files. This document does not report results, does not inspect
outcomes, and does not upgrade any theorem truth status.

## Design Principles

- Keep discovery cases out of confirmation: `C0-C5`, `C5_DAG`, `BIX1-SAT`,
  and `BIX2-PERSIST` can inspire mechanisms but cannot become held-out
  evidence.
- Separate structural/algebraic candidates from executable prefixes. A CRP,
  siphon, state-equation NIS, or recorder-transformed marking is not an IMS
  result until reachability and semantic mapping obligations are checked.
- Preserve negative results: unreachable candidates, bridge refusals, and
  baseline inapplicability are planned outcomes, not cleanup targets.
- Treat `L30`, `L31`, `L32/L33`, `L34/L35`, and `B05` as comparators with
  explicit assumptions, not theorem donors.

## Candidate G4 Cases

| Case ID | Family | Purpose | Prediction class | B status |
| --- | --- | --- | --- | --- |
| `G4_CRP_S4PR_AGREE` | `G4-CRP-S4PR-AGREE` | Restricted S4PR overlap where IMS wait-snapshot/core, S4PR CRP, and executable prefix should agree. | `partial_deadlock_bridge_agreement` | preregistered candidate |
| `G4_CRP_UNREACHABLE_CANDIDATE` | `G4-CRP-UNREACHABLE-CANDIDATE` | Structural/algebraic CRP or siphon candidate exists, but legal firing sequence or IMS prefix is absent. | `unreachable_candidate` | preregistered candidate |
| `G4_CRP_OUTSIDE_S4PR` | `G4-CRP-OUTSIDE-S4PR` | BAS blocked-unload, AGV occupancy/reservation, or AND/OR request violates S4PR/CRP assumptions. | `not_applicable` | preregistered candidate |
| `G4_RECORDER_TARGET_QUANTIFICATION` | `G4-RECORDER-TARGET-QUANTIFICATION` | `L32/L33` recorder-place transformation obligation for a fixed original target and fixed recorder counts. | `ordinary_and_fixed_target_reachable_with_distinct_shortest_witnesses` | preregistered candidate |
| `G4_L30_RESOURCE_BASELINE` | `G4-L30-RESOURCE-BASELINE` | Finite-capacity S3PR/ENS3PR resource-configuration comparator using supplied inequalities only. | `sufficient_conditions_satisfied` | preregistered candidate |
| `G4_B05_SUPERVISOR_COMPARATOR` | `G4-B05-SUPERVISOR-COMPARATOR` | Small explicit finite-LTS monitor-cover comparator plus independent finite-state supervisor baseline. | `two_monitor_legal_preserving_cover` | preregistered candidate |
| `G4_IMS_PARAMETER_GRID` | `G4-IMS-PARAMETER-GRID` | Ten held-out bidirectional BAS grid cells. | `acyclic_controls_safe_and_bidirectional_cells_structurally_exposed` | preregistered candidate |
| `G4_MEDIUM_ISLAND_REBUILD` | `G4-MEDIUM-ISLAND-REBUILD` | Independently specified three-island BAS/AGV rebuild. | `transport_inclusive_closed_core_exposure` | preregistered candidate |
| `G4_ADVERSARIAL_BOUNDARY` | `G4-ADVERSARIAL-BOUNDARY` | OR-of-AND, multi-capacity, AGV, and reservation boundary snapshot. | `closed_core_snapshot_with_nontransferable_or_and_semantics` | preregistered candidate |

## Ten-Cell Grid Prediction

The `G4_IMS_PARAMETER_GRID` row freezes ten boolean predictions. These are
pre-result predictions only.

| Cell | Expected reachable closed core |
| --- | --- |
| `G01_FWD_DAG` | `false` |
| `G02_REV_DAG` | `false` |
| `G03_BALANCED_TIGHT` | `true` |
| `G04_BALANCED_AGV2` | `true` |
| `G05_BALANCED_BUFFER2` | `true` |
| `G06_BALANCED_MACHINE2` | `true` |
| `G07_BALANCED_LOW_WIP` | `true` |
| `G08_FORWARD_SKEW` | `true` |
| `G09_FAST_RELEASE` | `true` |
| `G10_SLOW_TRANSFER` | `true` |

## Structural Validation Boundary

Current local structure evidence is limited to no-result JSON/document
inspection:

- `case_manifest.json` exists and lists nine canonical-json case hashes;
- nine `cases/confirmation/g4/cases/*.json` files exist and declare
  `held_out=true`, `status="PREREGISTERED"`, protocol
  `g4_confirmation_freeze_v1`, and `provenance="independent_preregistration"`;
- `predictions.json` contains one prediction for each of the nine case IDs and
  the ten grid-cell booleans above;
- `metrics_schema.json` contains the required metric IDs and freeze-time
  applicability reasons;
- `baseline_applicability.json`, `random_stream_manifest.json`,
  `runtime_lock.json`, `experiment_scripts_manifest.json`,
  `theory_manifest.json`, and `exclusions.json` are present;
- `FREEZE_ENTRY.json` is absent, so a complete freeze check must remain
  `NOT_FROZEN`.

The permitted pre-seal checks are schema, parser, hash, and structural
validation only. They may not enumerate held-out state spaces, classify
deadlocks, synthesize supervisors, solve CTMCs, run DES, compute rare-event
estimators, or inspect output directories.

## CRP Triad

The G4 CRP package must include all three rows below before any S4PR overlap
claim is allowed.

### 1. S4PR Agreement

Build a small S4PR-compatible IMS instance whose resource places, activity
places, initial marking, and firing semantics have an explicit bidirectional
map. The preregistered prediction may state agreement only inside this overlap:

- CRP marks the same partial-deadlock resource/activity set as the IMS local
  closed blocking core;
- the candidate marking has an explicit legal firing/event prefix verified
  against the source and IMS models; complete finite BFS/LTS enumeration is
  the independent oracle, while SBA is reported only as a comparator;
- the wait-snapshot diagnostic siphon is applicable only if `IMS-SIP^1`
  assumptions also hold.

### 2. Unreachable Structural/Algebraic Candidate

Build a paired S4PR-compatible instance where a siphon, CRP-shaped algebraic
candidate, or state-equation NIS is generated but no legal firing sequence from
the initial marking exists. Nonreachability must be closed by complete
finite-state BFS/LTS enumeration under a preregistered state bound, not by an
SBA return code alone. The expected report is a refusal:

- `structural_candidate_present=true`;
- `executable_prefix_present=false`;
- `ims_deadlock_claim=false`;
- no supervisor-cost win is credited for controlling the unreachable marking.

### 3. BAS/AGV/AND Outside S4PR

Build an IMS instance with one or more of:

- BAS blocked-unload holding after processing completion;
- AGV occupancy or hard reservation token required for the blocking kernel;
- AND/conjunctive request that cannot be reduced to a single S4PR resource
  request without changing semantics.

The expected report is not CRP disagreement. It is `not_applicable` unless an
explicit S4PR embedding is separately proved and hashed.

## Recorder Target-Quantification Obligation

`L32/L33`-style recorder transformations add output-only recorder places and
do not change original transition enabling. G4 must therefore avoid assuming a
negative preservation result. The case asks a narrower question: whether the
recorder construction, together with a fixed original IMS/Petri target marking,
closes the quantification needed by this project.

Required checks:

- every original executable trace used in the case maps into the instrumented
  model with the expected recorder count;
- the original target marking is mapped to a recorder target before solving
  reachability, rather than chosen after the fact;
- existential reachability of some recorder count is distinguished from
  reachability of the fixed count required by the original target;
- completion, partial-deadlock, and global-deadlock predicates are evaluated on
  the projected original marking, not on recorder-only state.

If all obligations are proved, the row is comparator agreement. If only one-way
trace preservation is available or the fixed-count target obligation remains
open, the row is a non-migration boundary. It is not a forced counterexample.

## L30 Resource-Configuration Baseline

The `L30` baseline is applicable only after an instance is represented as the
finite-capacity S3PR/ENS3PR class required by that paper. The planned question
is whether its minimum initial resource marking is a conservative sufficient
configuration relative to IMS exact reachable-threshold claims.

Allowed conclusions:

- `sufficient_configuration_agrees`;
- `sufficient_configuration_conservative`;
- `not_applicable_non_s3pr_ims_features`;
- `exact_threshold_not_claimed`.

Forbidden conclusions:

- `L30 proves IMS iff threshold`;
- `L30 eliminates need for executable reachability witness`;
- `L30 validates BIX2 outside its explicit three-resource family`.

## B05 Supervisor Comparator

The `B05` baseline is applicable only for small explicit Petri/RG overlap
instances where:

- the full reachability graph is generated and hashed;
- legal markings and first-met bad markings are identified;
- the covering/MCPP optimization result is recorded;
- P-semiflow control-place assumptions are checked.

If any condition fails, the baseline is reported as inapplicable. A successful
run compares structural compression and permissiveness only; it does not prove
that compact IMS supervisor synthesis is tractable.

## Metric Applicability Boundary

For the current B candidate:

- `supervisor_throughput_loss`, `supervisor_makespan_loss`,
  `supervisor_wip_change`, and `supervisor_due_date_risk_change` are
  inapplicable for every G4 case.
- `conditioned_path_mass` is inapplicable for every G4 case.
- `rare_event_efficiency` is inapplicable for every G4 case.
- CTMC exact probability and mean absorption time apply only to
  `G4_IMS_PARAMETER_GRID` and `G4_MEDIUM_ISLAND_REBUILD`.
- DES confidence intervals apply only to `G4_IMS_PARAMETER_GRID` and
  `G4_MEDIUM_ISLAND_REBUILD`.

## Seal Checklist

Before G4 can move from B candidate to C-sealed frozen, record:

- exact case manifest and SHA-256 hash;
- `FREEZE_ENTRY.json` with `confirmation_results_inspected=false`;
- S4PR/IMS embedding specifications and hashes;
- prediction sheet for every family above;
- baseline applicability sheet for `L30`, `L31`, `L32/L33`, `L34/L35`, and
  `B05`;
- explicit-prefix verifier and full finite BFS/LTS oracle for every case where
  reachability is part of the frozen estimand; SBA may be added as a separately
  reported comparator but cannot be the sole oracle;
- metric schema and negative-result reporting rules;
- runtime and command lock.

Until the C seal exists and passes the no-result freeze checker, G4 status
remains `B-PREREGISTRATION-CANDIDATE-PENDING-C-SEAL`.
