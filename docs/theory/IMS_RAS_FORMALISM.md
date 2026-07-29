# IMS-RAS Formalism

## Scope

`IMS-RAS` is a finite-batch resource allocation model for manufacturing-island
systems with finite buffers, machines, AGVs, reservations, and blocking after
service. The first paper excludes failures, preemption, dynamic order insertion,
and infinite exogenous arrivals.

## Primitive Sets

- `J`: finite jobs.
- `R`: reusable resources, partitioned into machines, buffers, AGVs, and
  optional reservation resources.
- `cap(r)`: positive integer capacity for every resource `r`.
- `O_j`: finite ordered operations for job `j`.
- `route(j, k)`: resource requests, processing activity, transport activity,
  and release obligations for operation `k`.
- `E0`: zero-time closure events.
- `Et`: timed events with rates or phase-type clocks in `IMS-CTMC`.

## State Variables

An `IMSState` records:

- resource occupancy counts;
- job-held resources;
- pending requests;
- route stage for every unfinished job;
- blocked machine completions;
- blocked AGV unloads;
- in-transit reservations;
- enabled zero-time events;
- timed event calendar or CTMC transition rates.

Capacity feasibility requires occupancy plus hard reservations never exceed
capacity. This rule applies to all entry and transport admission events; the old
source-project ambiguity where first-stage release bypassed reservation
accounting is deliberately excluded.

## Blocking After Service

Machine completion is split into two semantic outcomes:

- if the next buffer/resource admits the job, completion releases the machine
  and advances the job;
- if the destination is full, the job remains on the machine in
  `blocked_complete` and the machine remains occupied.

AGV arrival is analogous:

- if the destination input admits the job, unload releases the AGV and consumes
  the reservation;
- if the destination input is full, the job remains on the AGV in
  `blocked_unload` and the AGV remains occupied.

## Zero-time Closure

Every observed state is first closed under enabled zero-time events in a fixed
deterministic order:

1. release blocked machines whose destinations now admit;
2. unload blocked AGVs whose destinations now admit;
3. start enabled machine processing;
4. dispatch enabled AGV moves from output buffers.

A state is stable when no zero-time event is enabled. Deadlock and CTMC
transitions are evaluated only on stable states. If closure order affects the
stable state, the model is ill-formed unless a confluent closure proof or a
tie-breaking policy is supplied.

## Terminal Classes

- `complete`: every job has reached its terminal route stage and no resources
  are held.
- `operational deadlock`: stable, incomplete, and no timed or zero-time event can
  eventually release a blocked chain under current policy.
- `calendar-empty terminal block`: stable, incomplete, and the event calendar is
  empty. This is not a horizon failure; it is an auditable terminal state.
- `local deadlock`: a closed blocked subset exists while unrelated jobs may
  still complete.
- `quasi-deadlock`: progress is possible only through a policy choice or
  stochastic event outside the closed subset.
- `nonblocking`: every reachable state has at least one admissible continuation
  to completion under the supervisor.

## Finite Transition System

For a finite `IMS-RAS`, closure induces a finite transition system
`T = (S, s0, A, ->, S_complete, S_dead)`. Timed events become labels in `A`.
Uncontrolled processing completions are uncontrollable; release, dispatch,
transport choice, and reservation admission are controllable when the physical
system can withhold them.

