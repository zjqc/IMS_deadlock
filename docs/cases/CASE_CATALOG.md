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

## Provisional Witnesses

`C5-independent-witness-v1` is only a minimal discovery witness. Its
`output_capacity=0` construction prevents a real AGV launch, so it is useful
only as a machine-waiting boundary counterexample. It is not the final medium
case and must not be described as an original `C5` from the old project.

The next C5 design target is `C5b-md-agv-hard-reservation`, with a genuine
AGV `blocked_unload` state and a paired hard-reservation versus weak-reservation
comparison.

## Frozen Confirmation Cases

No confirmation case is frozen yet. Freezing requires:

1. a parameter grid and inclusion rule;
2. a theorem prediction sheet;
3. baseline definitions;
4. metric definitions;
5. repository commit hash;
6. manifest hash of every case JSON file;
7. a signed entry in `FREEZE_PROTOCOL.md`.

