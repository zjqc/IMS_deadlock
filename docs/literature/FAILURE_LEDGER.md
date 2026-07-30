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

## F05. Taxonomy Saturation Is Bounded, Not a Priority Proof

- Claim to reject: bounded OpenAlex taxonomy saturation means the systematic
  literature review and full-text theorem verification are complete.
- Evidence: `CITATION_TRACE_LOG.md` records scope-bounded taxonomy saturation in
  R2/R3 and R7/R8. The later L30-L35/B05 batch closes the current
  theorem-locator queue, but other DOI-verified entries remain
  metadata/context only and OpenAlex is not complete.
- Consequence: G1 is `PASS (scope-bounded)`, not a systematic-review,
  exhaustiveness, or scientific-priority certificate. Every theorem actually
  used still requires its recorded full-text locator and migration boundary.

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
  recorded in `SOURCE_VERIFICATION.md`; the same restriction was applied to
  B05 before its supplied full text was inspected and remains the rule for all
  future sources.

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

## F09. Fresh Reachability Literature Narrows G1 To Scope-bounded PASS

- Claim to reject: bounded taxonomy saturation or full-text extraction proves
  scientific priority.
- Evidence: the 2026 freshness audit and later supplied full texts located
  `L29-L35` and `B05`: MR2G/PDDP control, finite-capacity S3PR resource
  configuration, S4PR CRP partial-deadlock detection, reachability-decidable
  PN structure modification, BA/SBA legal-firing-sequence checks, and
  maximally permissive monitor supervision.
- Consequence: Rounds 7-8 and the full-text batch close G1 only as
  `PASS (scope-bounded)`. They do not authorize first, broad, general IMS, or
  general Petri-net bit-polynomial claims.
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
  necessary-but-not-sufficient gap and the full texts give BA/SBA methods for
  a given NIS; `L31` uses SBA to check CRP candidates, and `L32-L33` invoke
  BA/SBA-style reachability procedures after structure modification.
- Consequence: any algebraic detector used by IMS_deadlock must either provide
  a proved legal-event correspondence and a concrete reachable prefix, or be
  labeled a relaxation with measured false positives.
- Claim repair: `BIX1-SAT` and later parameterized families retain an exact
  finite-LTS witness; a future linear-equation baseline is compared against
  that witness rather than substituted for it. Any polynomial claim must handle
  `c` and numeric `n1`, not hide them.

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

## F12. Transformed Petri Nets Are Not Automatic IMS Plant Bridges

- Claim to reject: a recorder-place or structure-modified PN reachability
  result automatically proves an IMS operational-to-plant equivalence.
- Evidence: `L32-L33` give transformed-model trace lift/counter-state
  preservation and reachability procedures. The sink-recorder construction
  does not by itself answer how fixed original targets quantify over recorder
  counts, nor does it directly encode BAS, AGV occupancy, hard reservations,
  zero-time closure, OR-of-AND requests, or absorbing probability semantics.
- Consequence: the project must not claim reachability-decidable modeling is
  new, but it also must not assume the published transformations fail. Any
  projected bisimulation, completeness, or IMS preservation theorem must be
  separately stated and proved.
- Claim repair: use `L32-L33` as transparent transformed-PN baselines and test
  the exact IMS semantic bridge as an explicit proof obligation.

## F13. Parameter-polynomial Is Not Compact-input Bit-polynomial

- Claim to reject: `O(n*n1*(c*m+n^2))` proves polynomial-time reachability in
  the ordinary binary encoding of an arbitrary PN or compact IMS model.
- Evidence: `L34-L35` treat `c`, the directed-circuit count, and `n1`, the
  numeric sum of the fixed NIS entries, as parameters. `L32-L33` inherit that
  subroutine after structure modification. The L33 supplement's short
  circuit-count argument is not accepted here as a proof that every
  transformed instance has polynomially many directed circuits.
- Consequence: report BA/SBA as a given-NIS, parameter/pseudopolynomial
  baseline. Any standard bit-complexity theorem requires a separate input
  encoding, output convention, and bound on `c` and numeric `n1`.

## F14. Sufficient Resource Configuration Is Not an Exact Reachable Threshold

- Claim to reject: a liveness-guaranteeing minimum initial resource marking is
  automatically a necessary-and-sufficient WIP/capacity threshold for
  reachable IMS deadlock.
- Evidence: `L30` derives sufficient ENS3PR/SMS conditions and solves an ILP
  resource-configuration problem; its algorithm retains exponential SMS/ILP
  terms. It does not prove necessity of its configuration for the IMS
  operational semantics.
- Consequence: use L30 as a conservative comparator only. P3d/P3e exact iff
  thresholds remain family-specific and must retain both reachability
  witnesses above threshold and exclusion proofs below threshold.
