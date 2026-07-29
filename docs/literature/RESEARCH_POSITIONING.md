# Research Positioning

## Intended Contribution

IMS_deadlock should not be positioned as a software bundle that combines Petri
nets, DES supervisors, RAS safe states, queueing knots, and CTMC absorption.
Those are established theories. The publishable target is an IMS-specific
bridge:

1. a strict operational semantics for finite-batch manufacturing islands with
   BAS blocked-unload, finite input/output buffers, AGV occupancy, and
   reservations;
2. a minimal structural deadlock certificate on the zero-time-closed state;
3. a proven boundary between IMS blocking kernels, Petri-net siphons, RAS
   safety, and DES nonblocking supervision;
4. a probability layer that uses the same certificates as absorbing classes,
   not a disconnected simulation metric.

## Target Venues

- If the result yields general finite-state/DES/RAS theorems and complexity or
  maximal-permissiveness boundaries: `Automatica` or `IEEE TAC`.
- If the result is strongest as a manufacturing-island theory with rigorous
  case evidence and supervisor implementation: `IEEE T-ASE`.

## Claim Boundary

Allowed:

- IMS-RAS as a new formally defined subclass/family.
- Theorem ladder with explicit assumptions and counterexamples.
- Structural/probability/control bridge if each arrow is proved.

Not allowed:

- "A cycle implies deadlock" outside the single-instance restricted subclass.
- "Siphon theorem applies to IMS" without a Petri-net semantic equivalence.
- "Exact supervisor is scalable" without evidence.
- "Doob-h explains deadlock paths" without verified CTMC equations and source
  locators.

## Stop Condition

If G2 cannot produce at least one complete theorem chain:

`IMS operational semantics -> zero-time-closed finite transition system -> knot
certificate -> finite exact supervisor/probability baseline`

then the project must stop before building a large simulator and either:

- shrink to a provable IMS subclass, or
- reformulate the scientific question around a verified counterexample.
