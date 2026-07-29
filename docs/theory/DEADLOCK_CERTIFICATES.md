# Deadlock Certificates

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

A set of jobs and resources `K` is a closed blocking kernel in state `s` when:

1. every job in `K` is blocked by at least one resource in `K`;
2. every requested capacity unit in `K` is fully held or hard-reserved by jobs in
   `K`;
3. no zero-time release from outside `K` can satisfy a request in `K`;
4. all outgoing progress dependencies from jobs in `K` remain inside `K`.

Minimality is inclusion-minimality among kernels satisfying these four
conditions.

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

The deadlock-certificate theorem is:

> After zero-time closure, an IMS operational deadlock exists exactly when the
> state-dependent wait graph contains a closed blocking kernel satisfying the
> capacity and closure clauses.

The proof must show both directions and list model subclasses where the theorem
is intentionally weakened.

