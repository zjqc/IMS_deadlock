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
- Candidate attack / pending concrete model: `C4` is intended to test whether
  transport resources can close the blocking kernel even when the machine-only
  projection is deadlock-free. The concrete IMS model, reachable prefix, and
  certificate are still pending.
- Consequence: IMS formal state must include transport occupancy and
  reservations from the start.

## F05. Taxonomy Saturation Is Bounded, Full-text Gate Still Open

- Claim to reject: bounded OpenAlex taxonomy saturation means the systematic
  literature review and full-text theorem verification are complete.
- Evidence: `CITATION_TRACE_LOG.md` records scope-bounded taxonomy saturation in
  R2/R3, while several DOI-verified entries remain metadata/context only.
- Consequence: G1 can support G2 formalization, but final theorem claims still
  require exact full-text locators.

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

- Claim to reject: a bibliographically correct or abstract-accessible source
  can support equations before exact locators are recorded.
- Evidence: Ramadge-Wonham was initially held back until Theorem 7.1 and
  Proposition 7.1 were located. Narahari et al. was initially abstract-only,
  then upgraded on 2026-07-30 only after Sections 3, 3.1, 3.2, and 4 were
  inspected and `F=(I-T)^-1` / `G=FC` were located.
- Consequence: both are now theorem/equation anchors only for the exact scopes
  recorded in `SOURCE_VERIFICATION.md`; the earlier evidence restriction was
  correct and remains the rule for B05.

## F08. Tool Combination Is Not a Novelty Claim

- Claim to reject: combining Petri nets, a finite-state supervisor, an
  absorbing Markov model, and simulation is itself a top-journal contribution.
- Evidence: the verified literature already contains siphon-based liveness
  control, exact/maximally permissive finite-state or Petri supervisors,
  absorbing-chain deadlock metrics, AGV/transport deadlock models, and
  reachability/online avoidance.
- Consequence: the paper's novelty must be carried by proved interfaces and
  boundaries: an operational capacity-auditable certificate, the exact
  `IMS-SIP^1` state-induced diagnostic dual, a genuinely reachable
  manufacturing-island threshold family, and the probability/control layers
  built on the same absorbing certificate semantics. Every interface must
  retain its counterexample outside the declared subclass.

## F09. Fresh Reachability Literature Reopens the Saturation Stop Rule

- Claim to reject: the two bounded no-new-category rounds completed on
  2026-07-29 permanently close the novelty search.
- Evidence: the 2026 freshness audit found `L31`, whose official abstract
  claims critical resource-limit-pair equations that detect reachable partial
  deadlocks without a reachability tree. `L29` also supplies a current
  MR2G/PDDP partial-deadlock characterization and iterative liveness-enforcing
  control baseline, while `L30` directly addresses finite-capacity S3PR
  minimum-resource configuration.
- Consequence: Rounds 2-3 remain an auditable historical search result, but
  the stop counter resets. `L29-L31` must seed new bounded forward/backward
  rounds, and `L30-L31` require full-text assumption and proof extraction
  before any broad priority claim.
- Claim repair: the current contribution is only a candidate IMS-specific
  interface package. Its defensible unit is the joint operational semantics,
  capacity-auditable certificate/refusal boundary, restricted diagnostic
  dual, and shared probability/supervision interface—not generic reachable
  deadlock detection, generic graph equations, or generic capacity
  configuration.

## F10. A State-equation Solution Is Not an IMS Reachability Witness

- Claim to reject: a nonnegative integer solution of a Petri-net state equation
  is sufficient to establish a legal firing sequence or an executable IMS
  deadlock prefix.
- Evidence: the official abstracts for `L34-L35` explicitly identify the
  necessary-but-not-sufficient gap and introduce backward legal-firing-sequence
  methods; `L31-L33` make this boundary directly relevant to current
  reachability claims.
- Consequence: any algebraic detector used by IMS_deadlock must either provide
  a proved legal-event correspondence and a concrete reachable prefix, or be
  labeled a relaxation with measured false positives.
- Claim repair: `BIX1-SAT` and later parameterized families retain an exact
  finite-LTS witness; a future linear-equation baseline is compared against
  that witness rather than substituted for it.

## F11. Concealed Adaptation Is Not Scientific Novelty

- Claim to reject: changing notation, wording, proof order, or examples makes a
  published theorem or algorithm an original IMS result.
- Evidence: the relevant literature already supplies knots, siphons, state
  equations, legal-firing-sequence methods, finite-capacity resource
  configuration, supervisor synthesis, and absorbing-chain analysis.
- Consequence: every reused result follows
  `ADAPTATION_AND_ATTRIBUTION_PROTOCOL.md`; close structural following is cited
  at the statement/proof, not hidden in a distant bibliography entry.
- Claim repair: novelty is assessed after inherited components are removed. If
  no substantive IMS-specific theorem, counterexample, or interface remains,
  the project stops and reformulates.
