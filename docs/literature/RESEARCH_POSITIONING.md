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

The contribution is therefore an interface theorem package, not a toolbox
inventory:

`reachable IMS state`
`-> capacity-auditable closed blocking core`
`-> exact IMS-SIP1 wait-snapshot dual when and only when its assumptions hold`
`-> shared deadlock absorbing class for probability and supervision`.

The paired negative results are part of the contribution: conjunctive/OR
requests, multi-capacity residuals, control-only siphons, persistent-buffer
occupancy, and transport/resource projection each mark a boundary where one of
the arrows must be refused or replaced.

## Current Novelty Threats

Recent Petri-net work already provides iterative liveness-enforcing
supervisors, reduced/step-graph synthesis, finite-capacity S3PR resource
configuration, robust unreliable-resource control, and transport-equipment
deadlock handling. Accordingly, the paper must not claim that siphon control,
resource configuration, state-space reduction, AGV deadlock, or probability
of deadlock is generically new.

Two current comparators now delimit the structural claim especially sharply.
Lu et al. (`L29`) already characterize partial-deadlock markings through a
modified resource-requirement graph and PDDP constraints and synthesize a
liveness-enforcing Petri-net controller. Su et al. (`L31`) officially claim
reachable partial-deadlock detection through critical resource-limit-pair
linear equations without constructing a reachability tree; because only the
abstract has been verified, both its exact reachability meaning and its proof
boundary remain open. Until that full-text audit is complete, this project
must not claim to be the first reachable structural certificate or the first
reachability-free detector. Pang et al. (`L30`) similarly blocks a broad
"first finite-capacity threshold" claim until its equivalent-S3PR assumptions
are read in full.

Rounds 6-8 added a second reachability boundary. Su et al. (`L32-L33`)
officially claim Petri-net structure modifications intended to preserve modeled
functionality while making reachability decidable or polynomial-time
analyzable. The exact net classes and preservation relations remain unread in
full. Therefore IMS_deadlock must not claim that reachability-decidable
modeling, single-NIS state equations, or polynomial reachability after model
transformation are new. The state-equation/legal-firing-sequence lineage
(`L34-L35`) also requires every algebraic screen to retain an executable
reachability witness or an explicit relaxation label.

The defensible gap is narrower:

- existing structural candidates need not be reachable under the declared IMS
  operational semantics;
- a Petri resource graph need not expose BAS, AGV occupancy, hard reservation,
  zero-time closure, and OR-of-AND capacity evidence in one auditable object;
- classical probability and supervisor layers do not automatically use the
  same minimal operational certificate as their absorbing/forbidden boundary;
- restricted exact bridges are often asserted beyond their assumptions,
  whereas this project makes refusal and counterexamples machine visible.

The present `BIX1-SAT` result is therefore only a family-specific exact
reachability threshold under its explicit start/completion/drain semantics. It
is not evidence for a general IMS threshold and is not a priority claim over
finite-capacity S3PR configuration.

A later `BIX2-PERSIST` or other persistent-buffer result must be an
independently proved IMS family and a boundary case, not a renamed version of a
published finite-capacity or state-equation theorem.

All source use follows `ADAPTATION_AND_ATTRIBUTION_PROTOCOL.md`. Mature proof
devices and algorithms may be adapted aggressively when useful, but the source
statement, assumptions, locator, semantic map, and non-transferable boundary
must remain visible. Cosmetic rewriting is neither independence nor novelty.

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
- "The wait-snapshot diagnostic net is an IMS plant or S3PR net." It is a
  state-induced exact dual only inside `IMS-SIP^1`.
- "Exact supervisor is scalable" without evidence.
- "Doob-h explains deadlock paths" without verified CTMC equations and source
  locators.
- "First reachable partial-deadlock certificate" or "first
  reachability-free detector" before the `L31` full-text comparison.
- "First finite-capacity deadlock threshold" from the restricted `BIX1-SAT`
  theorem.
- "First polynomial/reachability-decidable Petri-net modeling method" while
  `L32-L33` exist and remain unread in full.
- Any novelty claim based only on renamed variables, reordered proof steps, or
  concealed source lineage.

## Stop Condition

If G2 cannot produce at least one complete theorem chain:

`IMS operational semantics -> zero-time-closed finite transition system -> knot
certificate -> finite exact supervisor/probability baseline`

then the project must stop before building a large simulator and either:

- shrink to a provable IMS subclass, or
- reformulate the scientific question around a verified counterexample.
