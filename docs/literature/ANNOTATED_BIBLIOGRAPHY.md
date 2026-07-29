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

Authorized use: abstract-only context for absorbing Markov modeling, mean time
to deadlock, mean number of finished parts before deadlock, and transient
deadlock-time distribution. No equation locator is recorded, so it stays out
of proof obligations.

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

## Verified Context Sources

Li, Z. W., & Zhou, M. C. (2004). Elementary siphons of Petri nets and their
application to deadlock prevention in flexible manufacturing systems.
https://doi.org/10.1109/TSMCA.2003.820576

The author PDF supports Sections 3, 4, 5, and 7 as context for elementary
siphon definitions, controllability discussion, algorithms, and FMS examples.
No theorem claim is migrated until exact theorem locators are extracted.

Liu et al. Siphon survey. https://doi.org/10.1016/j.ins.2015.08.037

Use as a siphon-review map only until stable locators are recorded. The wrong
DOI `10.1016/j.ins.2016.02.010` is rejected in `SOURCE_VERIFICATION.md`.

Viswanadham, Johnson, Narahari 1990 conference text.

Use only as provenance-limited inspiration for the `C4` three-resource
machine/AGV deadlock example. It is distinct from the journal paper
`Deadlock prevention and deadlock avoidance in flexible manufacturing systems
using Petri net models`, https://doi.org/10.1109/70.63257.

## Candidate Sources

The remaining DOI-verified rows in `LITERATURE_MATRIX.md` are backlog or
metadata candidates. They should not appear in theorem statements until their
full-text assumptions and locators are recorded.
