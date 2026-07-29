# C5 Reconstruction Protocol

## Source Boundary

The old manufacturing-island `work_case` is a semantic evidence source only.
This protocol does not copy its code, configuration values, random seeds,
labels, traces, or output metrics.

## Independent Mechanism

The independent C5 family is defined by mechanism, not by old file identity:

1. finite-batch jobs enter a manufacturing island;
2. at least two processing stages can request each other in opposite directions;
3. machines keep jobs when their output buffer is full;
4. AGVs keep jobs when a destination input buffer is full;
5. destination capacity checks include in-transit reservations;
6. event-calendar exhaustion with unfinished jobs is an explicit terminal
   blocked state.

## Paired Design

| Pair | Route family | Expected role |
| --- | --- | --- |
| `C5` | contains both `D -> M` and `M -> D` transitions | exposes closed blocking kernel under finite buffers and transport occupancy. |
| `C5_DAG` | removes the `D -> M` reverse route to enforce a common partial order | tests the acyclic-order sufficient condition and the old "delete backflow route" baseline. |

## Required Evidence for Acceptance

- model JSON with capacities, WIP, route family, transport resources, and
  timing labels;
- exact bounded finite-state enumeration output;
- shortest reachable deadlock prefix, which is zero length for the currently
  encoded initial blocked witness;
- minimality check for the blocking kernel;
- CTMC deadlock probability and mean absorption time for the finite generator,
  only after rates are independently encoded;
- independent DES simulation confidence interval;
- comparison against simple-cycle, knot, Banker, siphon where applicable,
  exact supervisor, and delete-backflow baselines.

## Known Non-final Witness

`C5-independent-witness-v1` is not final. Its `output_capacity=0` prevents a
real AGV dispatch and therefore cannot prove the AGV blocked-unload mechanism.
It remains in the ledger only as a boundary witness for machine-side
blocked-complete behavior.

The current executable `C5_DAG` is a structural repair witness, not a
confirmation case. It removes the reverse route, starts with the carrier free,
and exposes a finite completion path without fabricating CTMC rates.

## BIX Boundary

`BIX1-SAT` is the minimal reachable saturation slice for the P3d threshold:
it uses an empty initial holding state, explicit A/B start and completion
chains, and a witness prefix with no successful transfer. In that slice,
`D` and reservation token `V` disappear from the threshold only because no
successful transfer has consumed them before the deadlock witness.

`C5_DAG` only eliminates the specific `M-G` return mechanism represented by
the paired bidirectional slice. It is not a general deadlock-freedom claim for
manufacturing islands with persistent output buffers, missing drains,
alternative routes, or external calendar/guard boundaries.
