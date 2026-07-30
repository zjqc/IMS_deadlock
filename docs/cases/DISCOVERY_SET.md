# Discovery Set

The discovery set is allowed to falsify and repair definitions. It must not be
used for final performance claims after its results influence the theory.

## C0: Two-resource Minimal Deadlock

Two jobs each hold one singleton reusable resource and request the other. The
expected closure has no enabled zero-time or timed completion event that can
release either resource. This case establishes the certificate shape:

- held resource evidence;
- requested resource evidence;
- closed blocking kernel;
- shortest reachable prefix;
- no completion transition from the terminal state.

## C1: Cycle But Insufficient WIP

The static resource-order graph contains a directed cycle, but capacities or
WIP bounds prevent simultaneous occupation of every blocking predecessor. This
case invalidates the proposition "a directed cycle is sufficient for reachable
deadlock" outside tightly restricted singleton subclasses.

## C2: Global Resource Order DAG

Every route respects a common acyclic resource ranking. The proof obligation is
to construct a ranking potential that strictly decreases along wait chains or
rules out a closed blocking kernel. This is a sufficient condition, not a claim
that all deadlock-free IMS models admit such an order.

## C3: Multi-instance Counterexample

Multi-capacity resources can contain a static simple cycle while still having
free capacity, or contain a weakly connected no-sink component that is not a
terminal knot under the state-dependent wait graph. The discovery objective is
to pin down exactly when simple-cycle, sink-free WCC, and terminal-SCC criteria
diverge.

## C4: AGV Required

The machine-only projection removes transport occupancy and appears
nondeadlocked. Restoring AGV ownership and reservation edges creates a closed
blocking kernel. This case prevents a proof from silently projecting away the
transport layer.

## C5: M-D Bidirectional Independent Rebuild

C5 must be independently reconstructed from semantic facts, not copied from the
old project. The pair is:

- bidirectional family with both `D -> M` and `M -> D`;
- DAG repair family where the backflow edge is removed.

The target phenomenon is blocked completion or blocked unload caused by finite
buffers plus route-direction interaction. The final C5b must include a genuine
AGV `blocked_unload` state and a hard-reservation control comparison.

## BIX2-PERSIST: Persistent-buffer Ring and DAG Repair

The parameterized executable family is defined in
`BIX2_DISCOVERY_PROTOCOL.md`. It addresses the precise boundary left open by
`BIX1-SAT`: successful transfers may occupy `D`, so buffer capacity must enter
the blocking kernel.

The ring uses `M -> D -> Q -> M`; the paired repair deletes only `Q -> M`,
leaving `M -> D -> Q` plus explicit terminal release. The preregistered grid
tests the exact threshold and each one-dimension-below facet for singleton and
asymmetric multi-capacity triples. This is a discovery theorem attack and
cannot be reused as a held-out confirmation case.
