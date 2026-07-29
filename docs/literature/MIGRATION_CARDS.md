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

- Evidence type: `FULLTEXT-THEOREM`, adapted.
- 原定理: Lawley and Reveliotis (2001), Sections 3-5, establish SU-RAS safety NP-completeness, hard/easy boundary, and polynomial subclass discussion.
- 原假设: sequential resource allocation systems with formal safety states.
- IMS映射: define IMS safety as existence of a completion continuation from the zero-time-closed state under admissible controls.
- 缺失假设: output-buffer space, AGV occupancy, and reservations must be reduced to RAS claims/releases before applying SU-RAS reasoning.
- 适配命题/反例: restricted IMS subclasses may inherit safety-sequence logic; general IMS should inherit hardness warnings, not a simple polynomial test.
- 对应案例: `C1`, `C2`, frozen exhaustive family.

## M5. Nazeem-Reveliotis LES Benchmark

- Evidence type: `FULLTEXT-THEOREM`, benchmark.
- 原定理: Nazeem and Reveliotis (2011), Abstract and Sections II-III, support an offline/online two-stage approach for deploying maximally permissive LES in complex RAS.
- 原假设: finite RAS and liveness-enforcing supervisor framework.
- IMS映射: after finite IMS transition-system construction, compute small-model exact supervisors for comparison.
- 缺失假设: IMS closure and AGV/reservation semantics must be encoded before RAS LES machinery applies.
- 适配命题/反例: exact LES is a validation oracle and baseline, not the IMS paper's structural contribution.
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
- 缺失假设: absorbing IMS deadlock classes are not the same as ergodic A-B reactive-path conditioning.
- 适配命题/反例: write a separate absorbing-chain boundary-value theorem before using TPT path currents; do not claim TPT itself proves IMS deadlock risk.
- 对应案例: `C5` probability layer.

## M9. Ramadge-Wonham DES Benchmark

- Evidence type: `FULLTEXT-CONTEXT` in this library; pending theorem locator.
- 原定理: pending extraction from Ramadge and Wonham (1987).
- 原假设: finite DES language, controllable/uncontrollable event partition.
- IMS映射: dispatch, release, transport choice, and reservation become controllable events; processing completion is uncontrollable.
- 缺失假设: exact theorem locator and nonblocking specification must be recorded before theorem use.
- 适配命题/反例: treat as conceptual baseline until upgraded.
- 对应案例: all small supervisor benchmarks.

## M10. Narahari Absorbing Markov Layer

- Evidence type: `ABSTRACT` in this library; pending full-text equation locator.
- 原定理: not recorded yet.
- 原假设: official abstract indicates absorbing Markov modeling of deadlock performance.
- IMS映射: possible future basis for MTTD and transient distribution after full equations are located.
- 缺失假设: no equation locator is currently recorded.
- 适配命题/反例: cannot support IMS CTMC theorem statements yet.
- 对应案例: future `C0`, `C5` probability analysis.

## M11. Rare-event Splitting

- Evidence type: `FULLTEXT-CONTEXT`; heuristic/backlog.
- 原定理: no migrated theorem recorded from Cerou and Guyader (2007).
- 原假设: rare-event simulation setting.
- IMS映射: future estimator for low-probability deadlock events.
- 缺失假设: IMS-specific estimator, unbiasedness/variance assumptions, and source theorem locator.
- 适配命题/反例: keep out of first theorem ladder until probability layer is proven.
- 对应案例: later rare-event experiments.
