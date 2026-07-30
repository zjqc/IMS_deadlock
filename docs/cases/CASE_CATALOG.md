# Case Catalog

## Case Status Vocabulary

- `DISCOVERY`: may change definitions, hypotheses, and proof obligations.
- `FROZEN`: parameters, metrics, and inclusion rules are preregistered and must
  not be changed after evaluation starts.
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

## G4 Draft Confirmation Design

`G4_CASE_PREREGISTRATION.md` defines the next hard gate design. It is
`DRAFT-NOT-FROZEN`, not a result document. Its planned held-out families are:

| Family | Status | Purpose | Expected classification |
| --- | --- | --- | --- |
| `G4-CRP-S4PR-AGREE` | `DRAFT` | S4PR overlap where `L31` CRP, IMS core, and executable prefix should agree. | agreement only inside the hashed S4PR embedding. |
| `G4-CRP-UNREACHABLE-CANDIDATE` | `DRAFT` | Structural/algebraic CRP or siphon candidate without a legal firing sequence. | unreachable candidate; no IMS deadlock claim. |
| `G4-CRP-OUTSIDE-S4PR` | `DRAFT` | BAS/AGV/AND IMS semantics outside S4PR assumptions. | explicit not-applicable/refusal boundary. |
| `G4-RECORDER-TARGET-QUANTIFICATION` | `DRAFT` | Tests whether `L32/L33` recorder transformations close fixed-target quantification obligations. | comparator agreement if proved, otherwise non-migration boundary. |
| `G4-L30-RESOURCE-BASELINE` | `DRAFT` | Finite-capacity S3PR/ENS3PR resource configuration comparator. | sufficient/conservative baseline, not exact IMS threshold. |
| `G4-B05-SUPERVISOR-COMPARATOR` | `DRAFT` | Small full-RG compressed supervisor comparator. | permissiveness/structure comparator or inapplicable. |

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

No confirmation case is frozen yet. Freezing requires:

1. a parameter grid and inclusion rule;
2. a theorem prediction sheet;
3. baseline definitions;
4. metric definitions;
5. repository commit hash;
6. manifest hash of every case JSON file;
7. a signed entry in `FREEZE_PROTOCOL.md`.
