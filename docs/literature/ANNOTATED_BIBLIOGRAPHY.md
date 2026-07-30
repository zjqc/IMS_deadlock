# Annotated Bibliography

This bibliography separates proof-source anchors from contextual and candidate
sources. It intentionally records evidence limits instead of smoothing them
away.

## Proof-source Anchors

Ezpeleta, J., Colom, J. M., & Martinez, J. (1995). A Petri net based deadlock
prevention policy for flexible manufacturing systems. *IEEE Transactions on
Robotics and Automation, 11*(2), 173-184. https://doi.org/10.1109/70.370500

Authorized use: S3PR liveness/siphon-control boundary only. Recorded locators:
Corollary V.2, Theorem VI.1, and Section VI control policy. IMS migration still
requires a separate proof that an IMS subclass maps into the S3PR assumptions.

Ramadge, P. J., & Wonham, W. M. (1987). Supervisory control of a class of
discrete event processes. *SIAM Journal on Control and Optimization, 25*(1),
206-230. https://doi.org/10.1137/0325013

Authorized use: exact DES benchmark for controllability and supremal
controllable language. Recorded locators: Proposition 7.1 and Theorem 7.1 on
pp. 218-219. Use this as the language-theoretic baseline for IMS finite-state
supervisors, not as a structural deadlock certificate.

Fei, Z., Reveliotis, S. A., Miremadi, S., & Akesson, K. (2015). A BDD-based
approach for designing maximally permissive deadlock avoidance policies for
complex resource allocation systems. *IEEE Transactions on Automation Science
and Engineering, 12*(3), 990-1006.
https://doi.org/10.1109/TASE.2014.2369858

Authorized use: EFA/BDD framework and Theorem IV.1 on Algorithm 2 correctness.
It is an implementation benchmark, not the structural IMS contribution.

Lawley, M. A., & Reveliotis, S. A. (2001). Deadlock avoidance for sequential
resource allocation systems: Hard and easy cases. *International Journal of
Flexible Manufacturing Systems, 13*(4), 385-404.
https://doi.org/10.1023/A:1012203214611

Authorized use: SU-RAS safety complexity and the boundary between safety and
deadlock detection. The author PDF gives Theorem 1 on PDF p10 (SU-SAFE is
NP-complete), Proposition 2 on PDF p15 (intractable subclasses contain
deadlock-free unsafe states), and the capacitated-knot plus RC1/SR1/SR2/CB1
conditions on PDF pp18-24. None of these results transfers NP-completeness
directly to IMS-RAS.

Nazeem, A., & Reveliotis, S. A. (2011). A practical approach for maximally
permissive liveness-enforcing supervision of complex resource allocation
systems. *IEEE Transactions on Automation Science and Engineering, 8*(4),
766-779. https://doi.org/10.1109/TASE.2011.2159112

Authorized use: finite D/C-RAS LES benchmark. The author PDF gives
Proposition 1 and Definition 1 on PDF p5 for safe/unsafe state monotonicity and
maximal-safe/minimal-unsafe states; Section III gives the boundary-unsafe-state
implementation. IMS use requires a prior finite-state semantic encoding and a
proof that the paper's componentwise order applies.

Chen, Y. F., Li, Z. W., Khalgui, M., & Mosbahi, O. (2011). Design of a
maximally permissive liveness-enforcing Petri net supervisor for flexible
manufacturing systems. *IEEE Transactions on Automation Science and
Engineering, 8*(2), 374-393.
https://doi.org/10.1109/TASE.2010.2060332

Authorized use: bounded FMS Petri-net benchmark only. The author technical
report gives Assumptions 1-2 and Theorem 6 on report p19: under those
P-semiflow assumptions, the proposed method yields a maximally permissive
liveness-enforcing supervisor if such a supervisor exists. The 2012 correction
to Section V-B, https://doi.org/10.1109/TASE.2012.2183739, is part of the
audit trail. This does not establish maximum permissiveness for IMS-RAS before
the finite-state and Petri-net semantic bridges are proved.

Palmer, G. I., Harper, P. R., & Knight, V. A. (2018). Modelling deadlock in
open restricted queueing networks. *European Journal of Operational Research,
266*(2), 609-621. https://doi.org/10.1016/j.ejor.2017.10.039

Authorized use: finite-buffer queueing deadlock certificates. Theorem 1 gives
the knot equivalence; Theorem 2 gives the restrictions under which the no-sink
WCC shortcut works; the p6-p7 2/3-server counterexample is central to IMS case
`C3`.

Wu, N., & Zhou, M. (2001). Resource-oriented Petri nets in deadlock avoidance of
AGV systems. In *Proceedings 2001 ICRA. IEEE International Conference on
Robotics and Automation* (Vol. 1, pp. 64-69). IEEE.
https://doi.org/10.1109/ROBOT.2001.932531

Authorized use: AGV circuit/cycle-chain conditions and the corresponding
control law only within the paper's AGV Petri-net assumptions. Recorded
locators: Theorems 3.1, 3.2, 4.1, and 5.1. Public version recorded in
`SOURCE_VERIFICATION.md`.

Metzner, P., Schutte, C., & Vanden-Eijnden, E. (2009). Transition path theory
for Markov jump processes. *Multiscale Modeling & Simulation, 7*(3), 1192-1219.
https://doi.org/10.1137/070699500

Authorized use: Markov jump process TPT and the discrete committor equations in
Appendix subsection "Discrete Committor Equations", pp. 1216-1217. Its
assumptions are ergodic Markov jump processes and A-B reactive paths; it does
not directly prove absorbing IMS-deadlock results.

Narahari, Y., Viswanadham, N., & Krishna Prasad, K. R. (1990). Markovian
models for deadlock analysis in automated manufacturing systems. *Sadhana,
15*, 343-353. https://doi.org/10.1007/BF02811330

Authorized use: historical absorbing-chain probability anchor. The full
article gives the finite transient/absorbing DTMC partition and fundamental
matrix `F=(I-T)^-1` in Section 3 (journal pp. 346-348), mean time to deadlock
in Section 3.1, absorption probabilities `G=FC` in Section 3.2, and the
transient time-to-deadlock distribution in Section 4 (journal pp. 350-351).
The paper treats CTMC measures through the embedded chain. It does not source
the project's competing-absorption committor sensitivity or Doob-h theorem.

Corstanje, M., & van der Meulen, F. (2025). Guided simulation of conditioned
chemical reaction networks. *Statistical Inference for Stochastic Processes*.
https://doi.org/10.1007/s11203-025-09326-9

Authorized use: primary Doob-style conditioned CT jump-process baseline for the
probability layer. Recorded locators: Section 3.1, Eq. 3.1, Eq. 3.3, Appendix D.
This source supports the change-of-measure and conditioned-generator formulas,
but the IMS absorbing-boundary adaptation remains separate.

Cerou, F., & Guyader, A. (2007). Adaptive multilevel splitting for rare event
analysis. *Stochastic Analysis and Applications, 25*(2), 417-443.
https://doi.org/10.1080/07362990601139628

Authorized use: rare-event estimator benchmark under the paper's assumptions.
Journal p422 (PDF p7) states Hypothesis H and Theorem 1 on almost-sure
consistency; journal p425 (PDF p10) gives Theorem 2 on asymptotic normality and
variance. The one-dimensional strongly Markov, continuity, and score
assumptions must be re-established before using the result for IMS deadlock.

Lu, Y., Chen, Y., Hadjicostis, C. N., & Li, Z. (2026). Efficient iterative
deadlock prevention for flexible manufacturing systems utilizing modified
resource requirement graphs. *Automatica, 183*, 112631.
https://doi.org/10.1016/j.automatica.2025.112631

Authorized use: primary current comparator for structural partial-deadlock
detection and iterative Petri-net control. Publisher full text gives
Definition 3 for the modified resource requirement graph, Definition 4 for
safe places, Theorem 1 for the PDDP characterization, Algorithm 1 for
iterative control-place insertion, and Theorem 2 for liveness of the
controlled net. The method does not claim a maximally permissive supervisor;
its polynomial numbers of ILP variables/constraints do not make ILP solution
polynomial time. It does not provide the IMS operational/Petri/probability
interface, but it rules out novelty claims based merely on a holder/request
graph, an ILP deadlock candidate, or iterative control places.

Pang et al. (2025). Deadlock prevention in flexible manufacturing systems: A
verification-free resource configuration approach for liveness of
finite-capacity S3PR. https://doi.org/10.1177/01423312251369553

Authorized use: DIRECT comparator for finite-capacity S3PR/ENS3PR resource
configuration; ADAPTED only after an IMS subclass is encoded as the paper's
finite-capacity S3PR/ENS3PR; NONTRANSFERABLE to general IMS BAS, AGV,
reservation, closure, OR-of-AND, or probability/control semantics. Recorded
locators: PDF p3 Definition 1, p4 Definitions 2-3, p5 Definitions 4-6 and
Theorems 1-3, p6 Algorithm 1, and pp7-8 complexity. The result is sufficient
resource configuration, not an exact IMS iff threshold.

Su et al. (2026). A Novel Petri Net-Based Deadlock Detection Method for
Automated Manufacturing Systems. https://doi.org/10.1109/TASE.2026.3689269

Authorized use: DIRECT comparator for S4PR CRP partial-deadlock detection;
ADAPTED to IMS only through an explicit IMS-to-S4PR semantic map and reachable
prefix proof; NONTRANSFERABLE to IMS operational certificates without that
bridge. Recorded locators: PDF p4 Definitions 5-6, p5 Definitions 7-8 and
Theorem 1, p6 Definition 10 and Theorems 2-4, p7 SBA/Algorithm S3 discussion,
and supplement pp1-10 with proofs and Algorithms S1-S4. CRP equations generate
candidate partial deadlocks; reachability is still checked with SBA.

Su, Zhou, Qi, & Wisniewski (2025). A Reachability-Decidable Petri Net Modeling
Method for Discrete Event Systems. https://doi.org/10.1109/TSMC.2024.3473851

Authorized use: DIRECT comparator for reachability-decidable transformed-PN
modeling; ADAPTED only as a transparent baseline after the IMS-to-PN semantics
and recorder-count target quantification are fixed; NONTRANSFERABLE as an
automatic IMS operational-to-plant bridge. Recorded locators: PDF p3 Theorems
1-2, pp4-5 Algorithm 1 and Theorem 3, pp5-7 Theorems 4-8 and Algorithm 2, and
p8 Algorithm 3 and Theorem 11. The audit treats the main preservation as
trace lift/counter-state preservation for the transformed model.

Su, Zhou, Qi, Albeshri, & Abusorrah (2025). A Structure-Modification-Based
Petri Net Modeling and Reachability Analysis Method for Automated
Manufacturing Systems. https://doi.org/10.1109/TASE.2025.3588429

Authorized use: DIRECT AMS PN structure-modification comparator; ADAPTED only
after an IMS plant-to-PN map and projected completeness theorem are supplied;
NONTRANSFERABLE as a general IMS bisimulation. Recorded locators: PDF p3
Theorems 1-2, p4 Theorems 3-4, p5 Algorithm 1 and Theorems 5-6, pp6-7
Theorems 7-10 and Algorithm 2, plus supplement p1. The preservation set covers
reachability/liveness/persistence/repetitiveness and original siphon/trap
structure; boundedness may change after modification. Algorithm 2 uses SBA
with `O(n*n1*(c*m+n^2))`, so compact-input bit-polynomial claims remain
prohibited.

Su et al. (2023). A State-Equation-Based Backward Approach to a Legal Firing
Sequence Existence Problem in Petri Nets.
https://doi.org/10.1109/TSMC.2023.3241101

Authorized use: DIRECT source for the NIS-to-LFS false-positive boundary and
SBA baseline for a given NIS; ADAPTED only after IMS events are encoded as PN
firings; NONTRANSFERABLE to general IMS reachability. Recorded locators: PDF
pp3-5 Theorems 1-6, pp5-8 Algorithms 1-5, and pp7-8 complexity
`O(n*n1*(c*m+n^2))`, with explicit `c` and numeric `n1` caveats.

Su et al. (2023). A Backward Algorithm to Determine the Existence of Legal
Firing Sequences in Ordinary Petri Nets.
https://doi.org/10.1109/LRA.2023.3246384

Authorized use: DIRECT ordinary-PN BA baseline and necessary-not-sufficient
state-equation boundary; ADAPTED only after ordinary-PN encoding; NONTRANSFERABLE
as an IMS deadlock theorem. Recorded locators: PDF pp2-3 Theorems 1-5,
pp4-6 Algorithms 1-5, p6 complexity `O(n*n1*(c*m+n^2))`, and p7 conclusion.

Chen, Y. F., & Li, Z. W. (2011). Design of a maximally permissive
liveness-enforcing supervisor with a compressed supervisory structure for
flexible manufacturing systems. *Automatica, 47*(5), 1028-1034.
https://doi.org/10.1016/j.automatica.2011.01.070

Authorized use: DIRECT maximum-permissiveness and monitor-compression
benchmark for Petri-encodable FMS instances; ADAPTED only after full RG
legal/forbidden partition and monitor/P-semiflow expressibility are fixed;
NONTRANSFERABLE as a scalable IMS supervisor theorem. Recorded locators: PDF
p3 Definitions 1-3, p4 MCPP and Algorithm 1, p5 Theorem 1 and complexity
limitations. The paper depends on full RG data and an NP-hard MCPP.

## Verified Context Sources

Li, Z. W., & Zhou, M. C. (2004). Elementary siphons of Petri nets and their
application to deadlock prevention in flexible manufacturing systems.
https://doi.org/10.1109/TSMCA.2003.820576

The author PDF supports Sections 3, 4, 5, and 7 as context for elementary
siphon definitions, controllability discussion, algorithms, and FMS examples.
No theorem claim is migrated until exact theorem locators are extracted.

Liu et al. Siphon survey. https://doi.org/10.1016/j.ins.2015.08.037

Use as a secondary siphon-theorem map. Publisher full text exposes Section 4,
Theorem 2 on persistent siphon marking as a sufficient ordinary-net
deadlock-free condition, Theorem 3 on unmarked places at an ordinary dead
marking, and Theorems 4-7 on generalized/controlled-siphon and S3PR-family
liveness statements. These are survey restatements, not a replacement for the
original proofs or for the project-specific P2c bridge. The wrong DOI
`10.1016/j.ins.2016.02.010` remains rejected.

Viswanadham, Johnson, Narahari 1990 conference text.

Use only as provenance-limited inspiration for the `C4` three-resource
machine/AGV deadlock example. It is distinct from the journal paper
`Deadlock prevention and deadlock avoidance in flexible manufacturing systems
using Petri net models`, https://doi.org/10.1109/70.63257.

Viswanadham, N., Narahari, Y., & Johnson, T. L. (1990). Deadlock prevention
and deadlock avoidance in flexible manufacturing systems using Petri net
models. *IEEE Transactions on Robotics and Automation, 6*(6), 713-723.
https://doi.org/10.1109/70.63257

The full article is authorized as a historical modeling/control baseline: it
defines the Petri/GSPN setting, models the GE flexible manufacturing system
with blocked machines and finite input/output buffers, constructs a reachable
deadlock, and compares reachability-graph prevention with online
finite-look-ahead avoidance. No numbered theorem/proposition/lemma chain was
found, so it is not used as a siphon theorem or an IMS equivalence source.

## Candidate Sources

The remaining DOI-verified rows in `LITERATURE_MATRIX.md` are backlog or
metadata candidates. They should not appear in theorem statements until their
full-text assumptions and locators are recorded. The former L30-L35/B05
candidate batch has been upgraded by `FULLTEXT_AUDIT_L30_L35_B05.md`; it is no
longer an abstract-only request set.
