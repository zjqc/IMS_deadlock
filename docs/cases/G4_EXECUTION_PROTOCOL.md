# G4 Exact Execution Protocol

Status: `IMPLEMENTED-NOT-FROZEN`.

This document fixes the semantic boundary between held-out G4 JSON inputs and
post-freeze scientific execution. It is an implementation contract, not a
confirmation result.

## Separation of duties

The G4 workflow has three disjoint stages:

1. `confirmation.py` loads the preregistration envelope and rejects discovery
   contamination, duplicate JSON keys, path tricks, and result-bearing fields.
2. `g4_protocol.py` performs strict, family-specific structural decoding. It
   may construct typed values, verify hashes, and materialize no scientific
   observation.
3. `run_after_freeze` first requires `g4_freeze.py` to return `FROZEN`, then
   invokes the locked comparator, reachability, certificate, CTMC, supervisor,
   or DES backend.

The structural command is:

```text
python -m ims_deadlock.g4_protocol --root cases/confirmation/g4 validate
```

The post-freeze command for one case is:

```text
python -m ims_deadlock.g4_protocol --root cases/confirmation/g4 run <CASE_ID>
```

The five-command public `ims-deadlock` CLI is unchanged. Confirmation dispatch
is an internal module because discovery `CaseSpec` files and held-out
preregistration inputs have different contamination rules.

## Exact lowering table

| G4 family | Frozen source object | Locked execution carrier | Post-freeze backend |
| --- | --- | --- | --- |
| CRP agreement | explicit finite LTS, content-hashed S4PR embedding, supplied CRP pairs, external prefix claim, exact IMS target snapshot and resource map | `FiniteLTS`, `CRPEvidenceProfile`, `CaseSpec` target snapshot | independent BFS audit plus IMS certificate and exact mapped-resource equality |
| CRP unreachable candidate | explicit finite LTS with frozen candidate state and supplied evidence profile | `FiniteLTS`, `CRPEvidenceProfile` | independent complete BFS audit |
| CRP outside S4PR | explicit refusal profile plus `or_and_reservation_v1` exact generator parameters | `CRPEvidenceProfile`, generated `CaseSpec` | refusal audit plus IMS boundary diagnostics; no CRP generation |
| fixed recorder target | explicit finite LTS, target, recorder events and fixed count vector | `FiniteLTS` and immutable counter target | bounded augmented-state BFS |
| L30 resource baseline | capacity vector and supplied integer inequalities | `IntegerLinearInequality` tuple | sufficient-inequality evaluation only |
| B05 comparator | full finite LTS, legal states, first-met bad states and supplied candidates | `FiniteLTS`, `CandidateMonitor` tuple | exhaustive candidate cover plus exact finite-LTS supervisor baseline |
| IMS parameter grid | `bidirectional_bas_v1` and ten exact cells | generated `CaseSpec` and event-rate map | stable-LTS enumeration, certificate screens, derived CTMC, exact solve and fixed-stream Gillespie cross-check |
| medium island | `three_island_bas_v1` and one exact parameter vector | generated `CaseSpec` and event-rate map | same exact chain as the parameter grid |
| adversarial boundary | `or_and_reservation_v1` and one exact parameter vector | generated static `CaseSpec` | capacity-aware certificate and refusal diagnostics; no CTMC claim |

Every decoder requires exact JSON keys. Legacy aliases such as `from`/`to`,
missing `controllable`, `covers_bad_states`, prose-only generation semantics,
or unbound parameter ranges are rejected.

## Generated BAS semantics

`bidirectional_bas_v1` generates forward jobs

```text
machine_x -> {agv, buffer_y} -> machine_y
```

and reverse jobs

```text
machine_y -> {agv, buffer_x} -> machine_x.
```

At every stage, a job retains the current resource bundle after service
completion and releases it only atomically when the next bundle is acquired.
This is the project's finite BAS semantics. Machine capacity, buffer capacity,
AGV count, forward and reverse WIP, release rate, service rate, transfer rate,
and the state bound are frozen per cell.

`three_island_bas_v1` applies the same rule to exact `ABG`, `BAG`, and `AG`
routes over independently named machining, coating, inspection, buffer, and
AGV resources.

`or_and_reservation_v1` creates multi-capacity fixtures, two AGV resources,
inspection, and two hard reservation resources. Left and right jobs each have
two explicit alternatives, each alternative is a conjunctive demand, and
each branch transition enters a distinct persistent mode. The gate job holds
transport/inspection resources while requesting both reservations. This is a
snapshot boundary test; no path from an empty plant is inferred.

## Case-derived CTMC

For grid and medium cases only:

1. enumerate the complete stable LTS within the frozen bound;
2. classify complete states and certificate-bearing deadlock states;
3. refuse a truncated graph, multiple closure initial states, an absorbing
   initial state, an unclassified terminal class, or a missing event rate;
4. assign each stable arc its exact generated event rate;
5. sum parallel arcs into the transient generator or the two absorbing
   classes;
6. solve the finite competing-absorption system and run the fixed-stream
   Gillespie cross-check.

Thus the CTMC is case-derived, not a separately invented matrix. Event
self-loops that leave the stable semantic state unchanged are null events and
do not enter the off-diagonal generator.

## Frozen nonclaims

The implementation does not currently define:

- conditioned path mass, despite supporting a Doob-conditioned generator;
- importance sampling or rare-event efficiency;
- policy-conditioned due-date, makespan, throughput, or WIP response;
- source-paper CRP generation/SBA, L30 SMS enumeration, L32/L33 Petri
  transformation, L34/L35 BA/SBA, or B05 P-semiflow/MCPP reproduction.

Those metrics and baselines must be marked inapplicable at freeze time. They
cannot be enabled after observing confirmation outputs without a new
preregistration.
