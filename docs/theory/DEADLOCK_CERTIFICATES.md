# Deadlock Certificates

Canonical detailed definitions: `DEFINITIONS.md` and `THEOREM_LADDER.md`. This
file is the compact certificate object contract and uses the same set-valued
closure and multi-capacity semantics as `FORMAL_SEMANTICS.md`.

## State-dependent Wait Graph

For a stable state `s`, build a directed evidence graph:

- job nodes `J_s` for unfinished jobs that hold or request resources;
- resource nodes `R_s` for resources with positive capacity;
- hold edges `r -> j` when job `j` occupies or reserves resource `r`;
- request edges `j -> r` when job `j` cannot progress without resource `r`;
- blocked-unload and blocked-complete edges retain the current carrier as a
  held resource until the destination admits the job.

An edge must carry evidence: job id, route stage, resource id, capacity count,
and the semantic rule that created it.

## Closed Blocking Kernel

A set of jobs and resources `K` is a closed blocking kernel in stable state `s`
when the following independently checkable conditions hold:

1. every job in `K` is unfinished and blocked from all admissible local progress
   successors;
2. for every job in `K` and every legal alternative successor, at least one
   required capacity unit or reservation redemption is unavailable;
3. each unavailable unit is explained by residual capacity after subtracting
   actual holders and hard reservations under the model's declared reservation
   ontology;
4. the holders or reservers that explain the shortage are in `K` and cannot
   release the relevant unit without first taking an admissible progress
   successor already blocked by this same kernel;
5. no zero-time release, unload, cancellation, or closure event from outside `K`
   can satisfy any blocked request in `K`;
6. all outgoing progress dependencies from jobs in `K` are blocked by resources
   or token claims in `K`.

Minimality is inclusion-minimality among kernels satisfying these six
conditions.

For a global operational deadlock certificate, the kernel must additionally
cover all unfinished non-terminal activities, or equivalently prove global no
admissible successor after closure. It must also include explicit evidence for
at least one unfinished waiting or blocked activity. A kernel that covers only a
proper subset of unfinished activities certifies local deadlock or
quasi-deadlock, not global operational deadlock.

Two terminal cases are not automatically deadlock certificates:

- `calendar-empty terminal block`: stable and incomplete with no scheduled
  timed event, but without holder/request/release evidence for a waiting or
  blocked unfinished activity;
- `policy-induced stall`: no successor exists only because the supervisor or
  experiment policy disabled admissible controllable events.

Both must be recorded separately in verification output and cannot be promoted
to operational deadlock by the phrase "no successor" alone.

## Knot Relation

For singleton resources and selected finite-buffer queueing reductions, the
closed blocking kernel coincides with a terminal strongly connected component
or `knot` in the state-dependent blocking graph. In multi-capacity IMS models,
simple directed cycles are not sufficient; a terminal SCC must also account for
capacity saturation and reservation units.

## Certificate Object

A `DeadlockCertificate` must include:

- model id and state id;
- zero-time closure trace;
- kernel jobs and resources;
- hold/request evidence edges;
- capacity saturation proof;
- shortest reachable prefix when available;
- corresponding Petri siphon if the bridge assumptions hold;
- assumptions used by the detector;
- minimality result.

## Theorem Obligation

The candidate deadlock-certificate theorem is:

> After zero-time closure, an IMS operational deadlock exists exactly when the
> stable incomplete state contains a closed blocking kernel satisfying the
> independent capacity, holder/request, alternative-successor, and release
> clauses, and that kernel covers all unfinished non-terminal activities or
> otherwise proves global no admissible successor, with explicit evidence for
> at least one unfinished waiting or blocked activity. Calendar-empty terminal
> blocks and policy-induced stalls are excluded unless they satisfy the same
> holder/request/release evidence clauses.

The proof must show both directions and list model subclasses where the theorem
is intentionally weakened.

Forward obligation: from stable incomplete no-admissible-successor semantics,
construct the kernel and prove every shortage has holder/request/release
evidence. Reverse obligation: from a covering kernel, prove no admissible
successor exists without using the word "deadlock" inside the kernel definition
itself.
