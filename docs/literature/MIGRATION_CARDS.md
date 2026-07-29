# Migration Cards

Each card follows:

`原定理 -> 原假设 -> IMS映射 -> 缺失假设 -> 适配命题/反例 -> 对应案例`

Only cards backed by `FULLTEXT-THEOREM` sources can support theorem statements.
Other cards are explicitly marked as context or pending.

## M1. Palmer Knot Certificate

- Evidence type: `FULLTEXT-THEOREM`, adapted-direct after IMS wait-graph construction.
- 原定理: Palmer et al. (2018) prove that a state is deadlocked iff the state-dependent digraph `D(t)` contains a knot.
- 原假设: open restricted queueing network; finite buffers; blocked queues form `D(t)`.
- IMS映射: after zero-time closure, construct an IMS wait graph over blocked jobs, held resources, requested resources, output-buffer obligations, AGV occupancy, and reservation obligations.
- 缺失假设: IMS nodes are not queueing nodes by default; each edge type must be justified by the operational semantics.
- 适配命题/反例: prove knot equivalence only for the defined IMS wait graph. If any edge can release without an enabled IMS event, the closed-kernel implication fails.
- 对应案例: `C0`, `C3`, `C5`.

## M2. Palmer WCC Boundary

- Evidence type: `FULLTEXT-THEOREM`, adapted negative boundary.
- 原定理: Palmer et al. (2018) restrict the no-sink WCC shortcut to specific cases and give a 2-node 2/3-server counterexample.
- 原假设: restricted queueing network cases listed in Theorem 2.
- IMS映射: simple cycles and no-sink WCCs are screening features only.
- 缺失假设: IMS has multi-capacity resources and mixed machine/buffer/AGV/reservation nodes.
- 适配命题/反例: general IMS must use terminal SCC/knot certificates; simple-cycle sufficiency is allowed only as a separately proved single-instance corollary.
- 对应案例: `C1`, `C3`.

## M3. Ezpeleta S3PR Siphon Bridge

- Evidence type: `FULLTEXT-THEOREM`, adapted.
- 原定理: Ezpeleta et al. (1995), Corollary V.2, Theorem VI.1, and Section VI support S3PR liveness/siphon-control claims under S3PR assumptions.
- 原假设: sequential processes sharing reusable resource places in the S3PR construction.
- IMS映射: encode a restricted IMS subclass as sequential routes plus ordinary resource places for machines, buffers, AGVs, and static reservations.
- 缺失假设: BAS blocked-unload and dynamic reservation semantics may break ordinary S3PR structure.
- 适配命题/反例: minimal closed IMS blocking kernels may correspond to deadly siphons only in the restricted encoded subclass; outside it, only weaker one-way implications or counterexamples are expected.
- 对应案例: `C0`, `C4`, `C5`.

## M4. Lawley-Reveliotis Safety Boundary

- Evidence type: `FULLTEXT-THEOREM`, adapted boundary.
- 原定理: Lawley and Reveliotis (2001), PDF p10 Theorem 1, prove SU-SAFE NP-complete; PDF p15 Proposition 2 states that an SU-RAS class with intractable SU-SAFE contains deadlock-free unsafe states. PDF pp18-24 give the capacitated-knot definition and RC1/SR1/SR2/CB1 easy-class conditions.
- 原假设: SU-RAS with sequential single-resource acquisition, release of the previously held resource upon the next allocation, and the paper's reachability/safety semantics.
- IMS映射: define IMS safety as existence of a completion continuation from the zero-time-closed state under admissible controls.
- 缺失假设: output-buffer space, AGV occupancy, and reservations must be reduced to RAS claims/releases before applying SU-RAS reasoning.
- 适配命题/反例: use the source to prevent conflating deadlock detection with safety/nonblocking and to motivate a separate complexity proof. Do not transfer NP-completeness to IMS without a polynomial reduction into the declared IMS subclass.
- 对应案例: `C1`, `C2`, frozen exhaustive family.

## M5. Nazeem-Reveliotis LES Benchmark

- Evidence type: `FULLTEXT-THEOREM`, benchmark.
- 原定理: Nazeem and Reveliotis (2011), PDF p5 Proposition 1, give componentwise monotonicity of safe and unsafe D/C-RAS states; Definition 1 defines maximal safe and minimal unsafe states. Section III implements the maximally permissive LES through boundary reachable unsafe states.
- 原假设: finite D/C-RAS state space, the paper's componentwise state order, and an exact safe/unsafe partition.
- IMS映射: after finite IMS transition-system construction, compute small-model exact supervisors for comparison.
- 缺失假设: IMS closure and AGV/reservation semantics must be encoded before RAS LES machinery applies.
- 适配命题/反例: exact LES is a validation baseline after IMS closure and transport/reservation semantics are encoded. Proposition 1 cannot be assumed for the IMS state representation until its componentwise order is proved compatible.
- 对应案例: `C0`-`C5`, frozen confirmation set.

## M6. Fei BDD/EFA Correctness Benchmark

- Evidence type: `FULLTEXT-THEOREM`, benchmark.
- 原定理: Fei et al. (2015), Theorem IV.1, supports correctness of Algorithm 2 in the EFA/BDD framework.
- 原假设: finite-state RAS encoded into the paper's symbolic framework.
- IMS映射: a finite IMS model can be exported to a comparable symbolic/supervisor baseline after semantic reduction.
- 缺失假设: no direct proof for IMS-specific blocking kernels.
- 适配命题/反例: use as an algorithmic baseline for small/medium cases, not as theory replacement.
- 对应案例: frozen confirmation models.

## M7. Wu-Zhou AGV Circuit Conditions

- Evidence type: `FULLTEXT-THEOREM`, adapted/context for transport resources.
- 原定理: Wu and Zhou (2001), Theorems 3.1, 3.2, 4.1, and 5.1, give circuit/cycle-chain deadlock-free conditions and a control law for their AGV PN model.
- 原假设: resource-oriented PN model of AGV systems with the paper's circuit definitions.
- IMS映射: map IMS AGV occupancy and reservation conflicts to transport-resource subgraphs when the guidepath/reservation semantics fit the PN model.
- 缺失假设: IMS also contains machine processing, BAS unload, and finite buffers.
- 适配命题/反例: AGV theorem can support `C4` transport-resource irreducibility, but cannot certify complete IMS deadlock freedom alone.
- 对应案例: `C4`, AGV variants of `C5`.

## M8. Metzner-Schutte-Vanden-Eijnden TPT

- Evidence type: `FULLTEXT-THEOREM`, adapted with caution.
- 原定理: Metzner, Schutte, and Vanden-Eijnden (2009) develop TPT for ergodic Markov jump processes and give discrete committor equations in the appendix.
- 原假设: ergodic CTMC on discrete state space; A-B reactive paths.
- IMS映射: use committor equations as a template for deadlock-vs-completion risk after constructing an IMS-CTMC and handling absorbing boundaries.
- 缺失假设: absorbing IMS deadlock classes are not the same as ergodic A-B reactive-path conditioning; source locator is Appendix subsection "Discrete Committor Equations", pp. 1216-1217.
- 适配命题/反例: write a separate absorbing-chain boundary-value theorem before using TPT path currents; do not claim TPT itself proves IMS deadlock risk.
- 对应案例: `C5` probability layer.

## M9. Ramadge-Wonham DES Benchmark

- Evidence type: `FULLTEXT-THEOREM`.
- 原定理: Ramadge and Wonham (1987), Theorem 7.1 and Proposition 7.1.
- 原假设: finite DES language, controllable/uncontrollable event partition.
- IMS映射: dispatch, release, transport choice, and reservation become controllable events; processing completion is uncontrollable.
- 缺失假设: IMS must first be encoded as a finite-state transition system with a fixed controllable/uncontrollable partition.
- 适配命题/反例: use as the exact finite-state baseline for maximum permissiveness and nonblocking comparisons; do not infer structural deadlock certificates from language controllability.
- 对应案例: all small supervisor benchmarks.

## M10. Narahari Absorbing Markov Layer

- Evidence type: `FULLTEXT-THEOREM`, historical equation anchor.
- 原结果: Narahari et al. (1990), Section 3 (journal pp. 346-348), give the
  finite absorbing-DTMC partition and fundamental matrix `F=(I-T)^-1`;
  Section 3.1 gives mean time to deadlock; Section 3.2 gives absorption
  probabilities `G=FC`; Section 4 (journal pp. 350-351) gives the transient
  time-to-deadlock distribution.
- 原假设: finite transient/absorbing Markov chain; the stated CTMC measures use
  its embedded chain and state sojourn times.
- IMS映射: use as the historical metric lineage after a finite IMS stochastic
  generator and absorbing classes have been derived from the operational
  semantics.
- 缺失假设: the paper does not formulate the project's competing deadlock vs
  completion committor, generator sensitivity, conditional path law, or
  Doob-h transform.
- 适配命题/反例: P4 independently proves the IMS CTMC boundary-value and
  sensitivity equations; L16 corroborates classical absorption metrics but
  cannot replace L23/L28 or the project proof.
- 对应案例: `C0`, `C5` probability analysis after rate provenance is fixed.

## M11. Rare-event Splitting

- Evidence type: `FULLTEXT-THEOREM`, adapted with strict assumptions.
- 原定理: Cerou and Guyader (2007), journal p422 (PDF p7) Theorem 1, prove almost-sure consistency under Hypothesis H; journal p425 (PDF p10) Theorem 2 gives asymptotic normality and its variance.
- 原假设: the paper's one-dimensional strongly Markov process, attractive target, continuous trajectories, continuous hitting-score distribution, fixed survival proportion, and Hypothesis H.
- IMS映射: future estimator for low-probability deadlock events.
- 缺失假设: an IMS reaction coordinate/score that meets the theorem's hypotheses, treatment of a discrete finite-state CTMC, and a preregistered estimator/variance protocol.
- 适配命题/反例: the theorems justify AMS as a future baseline only after an IMS-specific assumption bridge; they do not yet establish unbiasedness, finite-sample coverage, or efficiency for IMS deadlock.
- 对应案例: later rare-event experiments.

## M12. Conditioned CT Jump Process

- Evidence type: `FULLTEXT-THEOREM`.
- 原定理: Corstanje and van der Meulen (2025), Section 3.1, Eq. 3.1, Eq. 3.3, Appendix D.
- 原假设: finite continuous-time jump process with conditioned observations or terminal hitting constraints.
- IMS映射: after finite IMS-CTMC construction, use the same change-of-measure idea to condition on deadlock vs completion absorbing events.
- 缺失假设: absorbing IMS boundary adaptation and non-explosive finite-state reduction must be proved separately.
- 适配命题/反例: the generator formula supports the probability layer; it does not by itself prove an IMS deadlock theorem.
- 对应案例: `C5` probability layer and future rare-event experiments.

## M13. Chen-Li-Khalgui-Mosbahi Petri-Net Supervisor

- Evidence type: `FULLTEXT-THEOREM`, benchmark with a published-correction caveat.
- 原定理: Chen et al. (2011), author technical report p19 Theorem 6, state that under Assumptions 1-2 the proposed deadlock-prevention method leads to a maximally permissive liveness-enforcing supervisor if such a supervisor exists.
- 原假设: bounded FMS Petri-net reachability model; the stated idle/resource-place minimal P-semiflows; monitor/P-invariant representation; existence of a maximally permissive supervisor expressible in the method's class.
- IMS映射: compare the exact finite IMS supervisor with a Petri-net monitor construction only after the P1 reachability-net representation and the required structural P-semiflows have been established.
- 缺失假设: the generic P1 reachability net is not automatically an FMS-oriented net with the paper's P-semiflows; BAS, AGV, reservations, and zero-time closure do not automatically preserve that structure.
- 适配命题/反例: use Theorem 6 as a restricted implementation benchmark, never as proof that every IMS maximum-permissive supervisor has a compact monitor representation. Consult the 2012 Section V-B correction before reproducing the affected construction text.
- 对应案例: future Petri-encodable restricted confirmation models; not the unrestricted `C4`/`C5` forms.

## M14. Liu et al. Siphon Survey Map

- Evidence type: `FULLTEXT-CONTEXT`, secondary theorem map.
- 原结果: Section 4, Theorem 2 states a sufficient persistent-marking
  condition for ordinary-net deadlock freedom; Theorem 3 states that the
  unmarked places at an ordinary dead marking form a siphon; Theorems 4-7 map
  controlled-siphon and S3PR-family liveness statements.
- 原假设: the particular ordinary/generalized Petri-net subclasses and
  controllability definitions cited by each surveyed theorem.
- IMS映射: use the ordinary siphon definition and theorem taxonomy to state
  exactly what the state-induced `IMS-SIP^1` wait-snapshot result resembles.
- 缺失假设: the survey supplies neither an IMS plant mapping nor an original
  proof that BAS, AGV, reservation, OR/AND requests, and closure semantics
  preserve those Petri subclasses.
- 适配命题/反例: P2c is an independent diagnostic-net theorem; control-only
  empty siphons and C4/C5 conjunctive requests show why the general reverse
  implication fails.
- 对应案例: `C0` exact diagnostic dual; `C4/C5` non-applicability.

## M15. Viswanadham-Narahari-Johnson Historical PN Controller

- Evidence type: `FULLTEXT-CONTEXT`, methods baseline.
- 原结果: the 1990 journal article constructs a Petri/GSPN model of the GE FMS
  with blocked machines and finite buffers, exhibits a reachable deadlock, and
  presents reachability-graph prevention plus online finite-look-ahead
  avoidance.
- 原假设: the paper's GE-FMS Petri model, routing/controller semantics, and
  enumerated or online look-ahead state information.
- IMS映射: historical comparator for modeling blocked machines/buffers and for
  distinguishing offline prevention from online avoidance.
- 缺失假设: no numbered theorem chain establishes a siphon equivalence,
  maximum permissiveness, or the IMS capacity-auditable certificate.
- 适配命题/反例: use only for historical positioning and case semantics; P1,
  P2, P2c, and P5 remain independent project results.
- 对应案例: `C4`, `C5`, and the exact finite-state supervisor baseline.

## M16. Lu-Chen-Hadjicostis-Li MR2G/PDDP Comparator

- Evidence type: `FULLTEXT-THEOREM`, competing baseline.
- 原定理: Definition 3 constructs the modified resource requirement graph;
  Definition 4 identifies safe operation places; Theorem 1 states the PDDP
  characterization of partial-deadlock markings; Algorithm 1 iteratively
  inserts control places; Theorem 2 establishes liveness of the controlled
  Petri net.
- 原假设: the paper's bounded FMS Petri-net structure, operation/resource
  places, resource-usage map, safe-place definition, and PDDP/place-invariant
  controller class.
- IMS映射: compare its resource-holder/request graph and per-iteration
  partial-deadlock constraint with the IMS capacity witnesses and intervention
  layer after an IMS state has a valid PN encoding.
- 缺失假设: the source does not encode the declared IMS BAS, AGV occupancy,
  hard-reservation, OR-of-AND, zero-time closure, or shared absorbing
  probability semantics; it does not claim maximum permissiveness.
- 适配命题/反例: do not claim that a capacity graph or iterative control-place
  synthesis is new. The project contribution must instead be the reachable
  operational certificate and explicitly delimited cross-layer interfaces.
  C4/C5 and control-only siphons test where the MR2G/Petri assumptions do not
  directly map.
- 对应案例: `C0` as restricted overlap; `C4/C5` as IMS-specific boundary;
  exact P5 supervisor as permissiveness comparator.

## M17. Su et al. Reachable Partial-Deadlock Threat

- Evidence type: `ABSTRACT`, migration blocked pending full read.
- 原主张: the official 2026 T-ASE abstract claims critical
  resource-limit pairs and linear equations detect reachable partial
  deadlocks for a useful Petri-net class without reachability-tree traversal.
- 原假设: not yet extracted from the full paper.
- IMS映射: potentially overlaps the project's reachability-certified local
  blocking core and must be compared before any general novelty claim.
- 缺失假设: full PN subclass, CRP construction, reachability proof,
  completeness, and complexity locators are not yet available in this library.
- 适配命题/反例: no theorem migration is authorized. Until full read, the
  project may claim neither first reachable structural certificate nor first
  avoidance of reachability-graph traversal.
- 对应案例: future restricted PN overlap benchmark; `BIX1-SAT` remains a
  family-specific exact threshold rather than a scalable general detector.
