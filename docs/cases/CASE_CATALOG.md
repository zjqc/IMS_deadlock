# Case Catalog

## Case Status Vocabulary

- `DISCOVERY`: may change definitions, hypotheses, and proof obligations.
- `B-PREREGISTRATION-CANDIDATE`: held-out inputs, predictions, metric
  applicability, baseline applicability, runtime, manifests, and exclusions
  have been drafted as a no-result preregistration candidate, but the C seal is
  not present.
- `FROZEN`: parameters, metrics, and inclusion rules are preregistered,
  sealed, and must not be changed after evaluation starts.
- `RETIRED`: kept as a negative result or boundary witness, not used to support
  a theorem.

## Discovery Cases

| Case | Status | Purpose | Expected certificate |
| --- | --- | --- | --- |
| `C0-two-resource-minimal` | `DISCOVERY` | Smallest two-job, two-singleton-resource deadlock. | one minimal closed blocking kernel and shortest reachable prefix. |
| `C1-cycle-but-insufficient-wip` | `DISCOVERY` | Shows that a resource graph cycle is not sufficient when WIP/capacity cannot populate the cycle. | no reachable deadlock; false-positive simple-cycle baseline. |
| `C2-global-order-dag` | `DISCOVERY` | Supports acyclic global resource request order as a deadlock-free sufficient condition. | rank function, no closed blocking kernel. |
| `C3-multi-instance-counterexample` | `DISCOVERY` | Separates simple cycles and weakly connected no-sink shortcuts from multi-capacity knot certificates. | multi-capacity state-dependent knot or explicit non-deadlock witness. |
| `C4-agv-required` | `DISCOVERY` | Machine projection is live/nondeadlocked, but adding AGV/reservation resources creates deadlock. | kernel contains AGV edge; projection-only certificate fails. |
| `C5-md-bidirectional-rebuild` | `DISCOVERY` | Independently reconstructs the M-D bidirectional manufacturing-island mechanism and pairs it with a backflow-deleted DAG variant. | blocked-complete/blocked-unload plus reservation-aware kernel. |
| `C5-md-dag-repair` | `DISCOVERY` | Removes the `D -> M` reverse route from the C5 pair and leaves an enabled forward release/progress path. | no closed blocking kernel; marked completion reachable in bounded LTS. |
| `BIX2-PERSIST` | `DISCOVERY` | Makes persistent buffer `D` a necessary member of a reachable `M -> D -> Q -> M` capacity kernel and pairs it with deletion of the `Q -> M` return. | ring: exact `{M,D,Q}` kernel; DAG: no kernel and marked completion reachable on the preregistered discovery domain. |

## G4 B Preregistration Candidate

`G4_CASE_PREREGISTRATION.md` records the current B-stage preregistration
candidate. It is `B-PREREGISTRATION-CANDIDATE-PENDING-C-SEAL`, not a result
document and not a C-sealed frozen bundle. The current candidate case IDs are:

| Case ID | Status | Purpose | Prediction class |
| --- | --- | --- | --- |
| `G4_CRP_S4PR_AGREE` | `B-PREREGISTRATION-CANDIDATE` | S4PR overlap where `L31` CRP, IMS core, and executable prefix should agree. | `partial_deadlock_bridge_agreement` |
| `G4_CRP_UNREACHABLE_CANDIDATE` | `B-PREREGISTRATION-CANDIDATE` | Structural/algebraic CRP or siphon candidate without a legal firing sequence. | `unreachable_candidate` |
| `G4_CRP_OUTSIDE_S4PR` | `B-PREREGISTRATION-CANDIDATE` | BAS/AGV/AND IMS semantics outside S4PR assumptions. | `not_applicable` |
| `G4_RECORDER_TARGET_QUANTIFICATION` | `B-PREREGISTRATION-CANDIDATE` | Tests whether `L32/L33` recorder transformations close fixed-target count obligations. | `ordinary_and_fixed_target_reachable_with_distinct_shortest_witnesses` |
| `G4_L30_RESOURCE_BASELINE` | `B-PREREGISTRATION-CANDIDATE` | Finite-capacity S3PR/ENS3PR supplied-inequality comparator. | `sufficient_conditions_satisfied` |
| `G4_B05_SUPERVISOR_COMPARATOR` | `B-PREREGISTRATION-CANDIDATE` | Small full-LTS monitor-cover comparator with independent finite-state supervisor baseline. | `two_monitor_legal_preserving_cover` |
| `G4_IMS_PARAMETER_GRID` | `B-PREREGISTRATION-CANDIDATE` | Ten held-out bidirectional BAS grid cells. | `acyclic_controls_safe_and_bidirectional_cells_structurally_exposed` |
| `G4_MEDIUM_ISLAND_REBUILD` | `B-PREREGISTRATION-CANDIDATE` | Independently specified three-island BAS/AGV rebuild. | `transport_inclusive_closed_core_exposure` |
| `G4_ADVERSARIAL_BOUNDARY` | `B-PREREGISTRATION-CANDIDATE` | OR-of-AND, multi-capacity, AGV, and reservation boundary snapshot. | `closed_core_snapshot_with_nontransferable_or_and_semantics` |

The grid row carries ten pre-result boolean predictions: `G01_FWD_DAG=false`,
`G02_REV_DAG=false`, and `G03_BALANCED_TIGHT` through
`G10_SLOW_TRANSFER=true`.

Current G4 metric applicability excludes all supervisor-cost metrics,
conditioned path mass, and rare-event efficiency. CTMC and DES metrics apply
only to `G4_IMS_PARAMETER_GRID` and `G4_MEDIUM_ISLAND_REBUILD`.

## Provisional Witnesses

`C5-independent-witness-v1` is only a minimal discovery witness. Its
`output_capacity=0` construction prevents a real AGV launch, so it is useful
only as a machine-waiting boundary counterexample. It is not the final medium
case and must not be described as an original `C5` from the old project.

The executable C5 pair now consists of `C5` and `C5_DAG`. `C5` is still a
discovery witness for bidirectional blocking, and `C5_DAG` is the paired
backflow-deleted repair. Neither case is a frozen confirmation fixture.

Deadlocked `C0` and `C5` may have only one reachable stable initial state in the
current structural batch. In those cases the shortest deadlock reachability
prefix is the zero-length initial-state witness.

## Frozen Confirmation Cases

No confirmation case is C-sealed frozen yet. The G4 bundle is a B
preregistration candidate. Its parameter grid, predictions, baseline and metric
definitions, runtime, and case hashes are present. Freezing still requires:

1. commit and push the complete B preregistration bundle;
2. create `FREEZE_ENTRY.json` with distinct implementation and
   preregistration commits plus every required artifact/case hash;
3. commit and push the C seal without changing a hashed prerequisite;
4. obtain `FROZEN` with zero errors from the no-result freeze checker.
