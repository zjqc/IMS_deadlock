# IMS-RAS Formalism

Canonical detailed document: `FORMAL_SEMANTICS.md`. This file is a compact
entry point and must not override the set-valued closure, reservation ontology,
or deadlock definitions in `FORMAL_SEMANTICS.md`, `DEFINITIONS.md`, and
`DEADLOCK_CERTIFICATES.md`.

## Scope

`IMS-RAS` is a finite-batch resource allocation model for manufacturing-island
systems with finite buffers, machines, AGVs, reservations, and blocking after
service. The first paper excludes failures, preemption, dynamic order insertion,
and infinite exogenous arrivals.

## Primitive Sets

- `J`: finite jobs.
- `R`: reusable resources, partitioned into machines, buffers, AGVs, and
  optional reservation resources or mapped hard-reservation claims.
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

Capacity feasibility follows one explicit reservation ontology:

- future-claim ontology: physical occupancy plus hard future claims never exceed
  the physical capacity, `occ(r)+hard_res(r)<=cap(r)`;
- token-resource ontology: reservation tokens are separate resources `v` with
  `target(v)=r`, `res(v)<=cap(v)`, and a separate proof that token redemption
  cannot overfill the physical resource.

This rule applies to all entry and transport admission events; the old
source-project ambiguity where first-stage release bypassed reservation
accounting is deliberately excluded. Soft reservations are not physical
capacity and must be represented with separate overbooking state.

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

The primary semantics is set-valued closure:

`Cl(s) = {stable successors reachable from s by zero-time events}`.

Every observed transition is evaluated after this closure. A fixed deterministic
priority order is only a named semantic variant, written `kappa(s)`, when
termination plus confluence is proven or when the priority/tie-breaking policy
is explicitly part of the model. Example priority variants may order release,
unload, start, and dispatch events, but that order is not the global IMS-RAS
definition.

A state is stable when no zero-time event is enabled. Deadlock and CTMC
transitions are evaluated only on stable states. If closure order affects the
stable state and no policy is supplied, the LTS must keep all stable successors.

## Terminal Classes

- `complete`: every job has reached its terminal route stage and no resources
  are held.
- `operational deadlock`: stable, incomplete, and no admissible timed,
  controllable, uncontrollable, or zero-time-closed successor exists.
- `calendar-empty terminal block`: stable, incomplete, and the event calendar is
  empty. This is not a horizon failure; it is an auditable terminal state.
- `local deadlock`: a closed blocked subset exists while unrelated jobs may
  still complete.
- `quasi-deadlock`: progress exists, but a candidate closed subset remains
  trapped under an explicitly defined blocking-equivalence relation; until that
  relation is formalized this is an informal discovery label.
- `nonblocking`: every reachable state has at least one admissible continuation
  to completion under the supervisor.

## Finite Transition System

For a finite `IMS-RAS`, set-valued closure induces a finite transition system
`mathcal T = (S_st, s0, A, ->, S_complete, S_dead)`. Timed events become labels in `A`.
Uncontrolled processing completions are uncontrollable; release, dispatch,
transport choice, and reservation admission are controllable when the physical
system can withhold them.
