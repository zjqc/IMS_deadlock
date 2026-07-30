# BIX2-PERSIST Discovery Protocol

## Status and Purpose

Status: `DISCOVERY-PROTOCOL-LOCKED`, not confirmation and not frozen.

This protocol was written before the BIX2 grid result was accepted as evidence.
The family is allowed to repair P3d's persistent-buffer boundary, but it cannot
enter the future confirmation set because its design and results may influence
the theorem.

The scientific question is whether a finite persistent buffer can be made a
necessary member of an exact reachable blocking kernel, instead of disappearing
from the `BIX1-SAT` threshold because no successful transfer occurs.

## Operational Family

Resources:

- machine `M` with capacity `c_M >= 1`;
- persistent finite buffer `D` with capacity `c_D >= 1`;
- downstream machine/transfer resource `Q` with capacity `c_Q >= 1`.

Jobs start from empty holdings:

- class A: acquire and hold `M`; uncontrollable processing completion requests
  `D`; handoff atomically acquires `D` and releases `M`; a later uncontrollable
  drain releases `D` and completes;
- class B: acquire and hold `D`; uncontrollable processing/availability
  completion requests `Q`; handoff atomically acquires `Q` and releases `D`; a
  later uncontrollable release of `Q` completes;
- class C in `ring` mode: acquire and hold `Q`; uncontrollable processing
  completion requests `M`; handoff atomically acquires `M` and releases `Q`; a
  later uncontrollable release of `M` completes;
- class C in `dag` mode: acquire and hold `Q`; uncontrollable processing
  completion is followed by release of `Q` and completion. There is no
  `Q -> M` request and no optional ring path.

Every start, request, and handoff uses one resource unit, and every unfinished
job holds at most one current resource unit in this family.

Every successful handoff has an explicit later release. A job is never marked
complete while retaining the resource acquired by that handoff.

## Predictions Fixed Before Grid Review

### H-BIX2-RING

In `ring` mode, a capacity-mediated global deadlock is reachable if and only if

`n_A >= c_M and n_B >= c_D and n_C >= c_Q`.

The predicted shortest witness class fills `M`, `D`, and `Q` with A, B, and C
holders, respectively, and then advances each holder to the request state. The
minimal `1/1/1` certificate must contain exactly resources `{M,D,Q}`.

### H-BIX2-DAG

Deleting the class-C `Q -> M` return creates the strict order `M < D < Q`.
With the explicit release chains above, no capacity-mediated global deadlock is
predicted reachable. At least one marked completion must be reachable for every
nonempty tested instance. This claim concerns this explicit family only; it is
not a general statement that deleting any backflow eliminates all finite-buffer
deadlocks.

## Preregistered Discovery Grid

Capacity triples are fixed to:

- `(1,1,1)`;
- `(2,1,1)`;
- `(1,2,1)`;
- `(1,1,2)`.

Equivalently, each capacity is at most 2 and the sum of capacities is at most 4.
For every capacity triple, test:

- the exact threshold point `(n_A,n_B,n_C)=(c_M,c_D,c_Q)`;
- the A-below facet `(c_M-1,c_D,c_Q)`;
- the B-below facet `(c_M,c_D-1,c_Q)`;
- the C-below facet `(c_M,c_D,c_Q-1)`.

After deduplication this yields 16 parameter points per mode and 32 rows across
`ring` and `dag`. The domain attacks every threshold dimension and three
asymmetric multi-capacity cases without including the known labeled-state
explosion at `(2,2,2;2,2,2)`.

## Evidence Rules

- Enumerate the exact stable finite LTS from the empty-holding initial state.
- A row is evidence only if enumeration is not truncated.
- Retain the shortest deterministic full-event prefix.
- Report certificate resources and capacity witnesses.
- In `dag` mode also report whether a marked completion is reachable.
- Any ring prediction mismatch, DAG deadlock, missing DAG completion, invalid
  instance, or truncation is retained in the failure ledger.
- Do not enlarge or shrink the grid after reading results. A later grid is a new
  protocol version and must report both versions.

## Interpretation Boundary

The three-resource ring is classical circular-wait structure and is not claimed
as a new graph idea. Its role is an IMS operational boundary theorem/checker:
it makes persistent `D` occupancy executable, capacity-auditable, reachable
from empty holdings, and paired with an exact structural repair under the same
event semantics. Any published proof device later used to strengthen it must
follow `docs/literature/ADAPTATION_AND_ATTRIBUTION_PROTOCOL.md`.
