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
| `C5b-bidirectional` | contains both `D -> M` and `M -> D` transitions | exposes closed blocking kernel under finite buffers and transport occupancy. |
| `C5b-dag-repair` | removes one direction to enforce a common partial order | tests the acyclic-order sufficient condition and the old "delete backflow route" baseline. |

## Required Evidence for Acceptance

- model JSON with capacities, WIP, route family, transport resources, and
  timing labels;
- exact finite-state enumeration output;
- shortest reachable deadlock prefix;
- minimality check for the blocking kernel;
- CTMC deadlock probability and mean absorption time for the finite generator;
- independent DES simulation confidence interval;
- comparison against simple-cycle, knot, Banker, siphon where applicable,
  exact supervisor, and delete-backflow baselines.

## Known Non-final Witness

`C5-independent-witness-v1` is not final. Its `output_capacity=0` prevents a
real AGV dispatch and therefore cannot prove the AGV blocked-unload mechanism.
It remains in the ledger only as a boundary witness for machine-side
blocked-complete behavior.

