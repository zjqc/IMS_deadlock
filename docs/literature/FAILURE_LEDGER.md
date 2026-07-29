# Failure and Counterexample Ledger

This ledger records failed assumptions, rejected sources, and theorem-boundary
attacks. Entries are evidence, not embarrassment; they protect the paper from
post-hoc theory edits.

## F01. Wrong DOI for Siphon Survey

- Claim: `10.1016/j.ins.2016.02.010` was a siphon survey.
- Finding: It resolves to an unrelated l1-gain paper.
- Correction: Use `10.1016/j.ins.2015.08.037` for the siphon survey candidate.
- Consequence: Any prior citation using the wrong DOI is invalid.

## F02. Simple Cycle Is Not a General Deadlock Certificate

- Claim to reject: if a resource/wait graph has a directed cycle, IMS is deadlocked.
- Evidence: Palmer et al. (2018) shows the stronger no-sink WCC shortcut has
  strict restrictions and gives a multi-server counterexample; multi-capacity
  IMS resources are at least as dangerous.
- Consequence: General IMS certificates must use terminal SCC/knot-like closed
  blocking kernels, with a simple-cycle corollary only for a single-instance
  restricted subclass.

## F03. No-sink WCC Shortcut Is Restricted

- Claim to reject: any weakly connected blocked component without a sink is a
  sufficient deadlock certificate.
- Evidence: Palmer et al. (2018), Theorem 2 restrictions and 2/3-server
  counterexample.
- Consequence: `C3` must be designed to attack this shortcut.

## F04. AGV/Reservation Cannot Be Dropped by Machine Projection

- Claim to reject: if the machine-only projection is deadlock-free, the IMS is
  deadlock-free.
- Evidence: AGV blocking examples and the planned `C4` construction show
  transport resources can close the blocking kernel.
- Consequence: IMS formal state must include transport occupancy and
  reservations from the start.

## F05. G1 Saturation Not Yet Achieved

- Claim to reject: the current literature search has completed two saturated
  citation rounds.
- Evidence: several DOI-verified entries remain metadata-only, and committor,
  rare-event, and AGV theorem sources are not yet full-text located.
- Consequence: G1 can support seed theory construction, not final paper claims.

## F06. Viswanadham 1990 Conference and Journal Records Were Mixed

- Claim to reject: the DOI-less AGV/machine example text and the IEEE T-RA
  journal paper are the same citation.
- Evidence: `10.1109/70.63257` resolves to the journal article `Deadlock
  prevention and deadlock avoidance in flexible manufacturing systems using
  Petri net models`, while the three-resource AGV example remains a
  provenance-limited conference text.
- Consequence: The example can inspire `C4`, but the journal paper must be
  separately read before it supports any theorem claim.

## F07. Context Sources Were Over-promoted

- Claim to reject: Ramadge-Wonham 1987 and Narahari et al. 1990 can support
  theorem statements in this library without recorded theorem/equation
  locators.
- Evidence: current records contain publication/abstract access but no stable
  theorem/equation locator.
- Consequence: Ramadge-Wonham is `FULLTEXT-CONTEXT` here, Narahari et al. is
  `ABSTRACT`, and both must be upgraded before theorem use.
